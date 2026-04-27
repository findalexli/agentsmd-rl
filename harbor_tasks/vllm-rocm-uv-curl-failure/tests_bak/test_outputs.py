"""
Task: vllm-rocm-uv-curl-failure
Repo: vllm-project/vllm @ b2bc736b1247a76e6ab1cfbe38ae39c3c307de40

Bug: `curl ... | sh` in docker/Dockerfile.rocm masks curl failures because
sh reads empty stdin and exits 0. Fix must save to file first, add retry,
and verify installation.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
TARGET = Path(REPO) / "docker" / "Dockerfile.rocm"


def _extract_uv_install_cmd() -> str:
    """Extract the RUN instruction containing astral.sh/uv/install.sh."""
    lines = TARGET.read_text().split("\n")
    result = []
    in_run = False

    for line in lines:
        stripped = line.strip()
        if not in_run:
            if stripped.startswith("RUN"):
                in_run = True
                result = [re.sub(r"^\s*RUN\s+", "", line)]
        else:
            result.append(line)

        if in_run and not stripped.endswith("\\"):
            full = "\n".join(result)
            if "astral.sh/uv/install.sh" in full:
                return full
            in_run = False
            result = []

    raise AssertionError("No RUN command containing astral.sh/uv/install.sh found")


def _write_script(path: Path, content: str):
    """Write an executable script."""
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _run_cmd_with_mocks(cmd_script: str, mock_dir: str) -> int:
    """Run the extracted command with mock_dir prepended to PATH."""
    env = os.environ.copy()
    env["PATH"] = f"{mock_dir}:{env['PATH']}"
    env["UV_INSTALL_DIR"] = "/usr/local/bin"
    r = subprocess.run(
        ["bash", "-c", cmd_script],
        env=env,
        capture_output=True,
        timeout=30,
    )
    return r.returncode


MOCK_SUCCESS_CURL = """\
#!/bin/bash
OUTPUT_FILE=""
for ((i=1; i<=$#; i++)); do
    arg="${!i}"
    if [ "$arg" = "-o" ] || [ "$arg" = "--output" ]; then
        next=$((i+1)); OUTPUT_FILE="${!next}"
    elif [[ "$arg" == --output=* ]]; then
        OUTPUT_FILE="${arg#--output=}"
    elif [[ "$arg" == -o* ]] && [ "${#arg}" -gt 2 ]; then
        OUTPUT_FILE="${arg:2}"
    fi
done
SCRIPT='#!/bin/sh
echo "Installing uv to ${UV_INSTALL_DIR:-/usr/local/bin}"
'
if [ -n "$OUTPUT_FILE" ]; then
    echo "$SCRIPT" > "$OUTPUT_FILE"; chmod +x "$OUTPUT_FILE"
else
    echo "$SCRIPT"
fi
exit 0
"""

MOCK_UV = """\
#!/bin/bash
if [ "${1:-}" = "--version" ]; then echo "uv 0.7.8"; fi
exit 0
"""

MOCK_FAIL_CURL = """\
#!/bin/bash
echo "curl: (7) Failed to connect to astral.sh port 443" >&2
exit 7
"""

MOCK_FAIL_UV = """\
#!/bin/bash
echo "uv: not installed" >&2
exit 127
"""


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dockerfile_exists():
    """docker/Dockerfile.rocm must exist and contain UV install command."""
    assert TARGET.exists(), f"{TARGET} not found"
    content = TARGET.read_text()
    assert "astral.sh/uv/install.sh" in content, "No UV install URL found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_curl_failure_propagates():
    """When curl fails, the UV install command must exit non-zero.

    Base bug: `curl ... | sh` — sh reads empty stdin and exits 0, masking curl's
    non-zero exit code. Fixed: curl writes to file first, so && propagates failure.
    """
    cmd = _extract_uv_install_cmd()
    with tempfile.TemporaryDirectory() as td:
        _write_script(Path(td) / "curl", MOCK_FAIL_CURL)
        _write_script(Path(td) / "uv", MOCK_FAIL_UV)
        rc = _run_cmd_with_mocks(cmd, td)
    assert rc != 0, (
        "curl failure was MASKED — command exited 0 despite curl failing. "
        "This is the core bug: curl|sh hides curl's exit code."
    )


# [pr_diff] fail_to_pass
def test_retry_flag_present():
    """The curl command must include --retry for transient failure recovery.

    Base: no --retry flag. Fix adds --retry N.
    """
    cmd = _extract_uv_install_cmd()
    assert "--retry" in cmd, (
        "No --retry flag in curl command — transient network failures will not recover"
    )


# [pr_diff] fail_to_pass
def test_verifies_uv_installed():
    """After install, the command must verify uv is actually available.

    Base: no verification — if install silently fails, uv is missing.
    Fix: adds `uv --version` (or similar check) at the end.
    """
    cmd = _extract_uv_install_cmd()
    # Run with successful curl but uv missing/broken
    with tempfile.TemporaryDirectory() as td:
        _write_script(Path(td) / "curl", MOCK_SUCCESS_CURL)
        _write_script(Path(td) / "uv", MOCK_FAIL_UV)
        rc = _run_cmd_with_mocks(cmd, td)
    assert rc != 0, (
        "Command succeeded even though uv is not installed. "
        "The fix should verify uv is available after installation."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_successful_install_works():
    """When curl succeeds, the UV install command must complete successfully."""
    cmd = _extract_uv_install_cmd()
    with tempfile.TemporaryDirectory() as td:
        _write_script(Path(td) / "curl", MOCK_SUCCESS_CURL)
        _write_script(Path(td) / "uv", MOCK_UV)
        rc = _run_cmd_with_mocks(cmd, td)
    assert rc == 0, f"Install failed even when curl succeeds (exit {rc})"


# [pr_diff] pass_to_pass
def test_settings_preserved():
    """UV_INSTALL_DIR and astral.sh URL must be preserved in the Dockerfile."""
    content = TARGET.read_text()
    assert re.search(r"UV_INSTALL_DIR.*?/usr/local/bin", content), (
        "UV_INSTALL_DIR not set to /usr/local/bin"
    )
    assert "astral.sh/uv/install.sh" in content, "astral.sh UV install URL missing"


# [static] pass_to_pass
def test_command_not_stub():
    """The UV install command must have real download + execute logic."""
    cmd = _extract_uv_install_cmd()
    lines = [l.strip().rstrip("\\").strip() for l in cmd.splitlines()]
    real = [l for l in lines if l and not l.startswith("#")]
    has_download = any("curl" in l or "wget" in l for l in real)
    has_execute = any(
        "sh " in l or "bash " in l or "install.sh" in l for l in real
    )
    assert has_download, "UV install command has no download step (curl/wget)"
    assert has_execute, "UV install command has no execute step (sh/bash)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI tests
# ---------------------------------------------------------------------------


def test_repo_ruff_check():
    """Repo's Python linting passes (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # ruff check passes on docker/ directory (no Python files but validates syntax)
    r = subprocess.run(
        ["ruff", "check", "docker/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_dockerfile_validate():
    """Repo's dockerfile validation passes (pass_to_pass)."""
    # Install dockerfile-parse if not available
    subprocess.run(
        ["pip", "install", "-q", "dockerfile-parse"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["python3", "tools/generate_versions_json.py", "--check"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Dockerfile validation failed:\n{r.stderr[-500:]}"


def test_repo_dockerfile_rocm_syntax():
    """Dockerfile.rocm has valid syntax and required directives (pass_to_pass)."""
    content = TARGET.read_text()
    # Check for basic Dockerfile requirements
    assert content.strip().startswith("#") or content.strip().startswith("FROM") or "ARG" in content, \
        "Dockerfile.rocm missing standard Dockerfile directives"
    # Verify there's a FROM statement
    assert "FROM" in content, "Dockerfile.rocm missing FROM directive"
    # Check for proper line continuation usage (backslashes should have content after)
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if line.rstrip().endswith("\\"):
            # Next non-empty line should exist and have content
            found_next = False
            for next_line in lines[i:]:
                if next_line.strip():
                    found_next = True
                    break
            assert found_next, f"Line {i} has continuation but no following content"


def test_repo_shellcheck():
    """Repo's shell scripts pass shellcheck linting (pass_to_pass)."""
    # Install shellcheck
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install shellcheck: {r.stderr[-500:]}"
    # Run shellcheck on repo's shell scripts using the pre-commit script
    r = subprocess.run(
        ["bash", "tools/pre_commit/shellcheck.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_actionlint():
    """Repo's GitHub Actions workflows pass actionlint (pass_to_pass)."""
    # Install actionlint
    subprocess.run(
        ["pip", "install", "-q", "actionlint-py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Run actionlint on GitHub workflow files (find them first to handle glob)
    import glob
    workflow_dir = Path(REPO) / ".github" / "workflows"
    workflow_files = list(workflow_dir.glob("*.yml"))
    if workflow_files:
        r = subprocess.run(
            ["actionlint"] + [str(f) for f in workflow_files],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Actionlint failed:\n{r.stderr[-500:]}"


def test_repo_dockerfile_graph():
    """Repo's Dockerfile dependency graph is up to date (pass_to_pass)."""
    # Run the update-dockerfile-graph script which validates graph consistency
    r = subprocess.run(
        ["bash", "tools/pre_commit/update-dockerfile-graph.sh"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Dockerfile graph check failed:\n{r.stderr[-500:]}"


def test_repo_spdx_headers():
    """Repo's Python files have SPDX license headers (pass_to_pass)."""
    # Install regex dependency if not available
    subprocess.run(
        ["pip", "install", "-q", "regex"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/check_spdx_header.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stderr[-500:]}"


def test_repo_init_lazy_imports():
    """Repo's root __init__.py uses lazy imports correctly (pass_to_pass)."""
    r = subprocess.run(
        ["python", "tools/pre_commit/check_init_lazy_imports.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lazy imports check failed:\n{r.stderr[-500:]}"


def test_repo_forbidden_imports():
    """Repo's Python files don't have forbidden imports (pass_to_pass)."""
    # Install regex dependency if not available
    subprocess.run(
        ["pip", "install", "-q", "regex"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/check_forbidden_imports.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Forbidden imports check failed:\n{r.stderr[-500:]}"
