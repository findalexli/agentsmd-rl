"""
Task: sglang-amd-ci-git-safe-directory
Repo: sgl-project/sglang @ 6f2b51ade1b1d072ee7e8d2727f1dbaec0f496ae
PR:   #21423

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
SCRIPT1 = f"{REPO}/scripts/ci/amd/amd_ci_start_container.sh"
SCRIPT2 = f"{REPO}/scripts/ci/amd/amd_ci_start_container_disagg.sh"
SCRIPTS = [SCRIPT1, SCRIPT2]


def _read_no_comments(path: str) -> str:
    """Read file, strip comment-only content from each line."""
    text = Path(path).read_text()
    lines = []
    for line in text.splitlines():
        stripped = re.sub(r"#.*", "", line)
        if stripped.strip():
            lines.append(stripped)
    return "\n".join(lines)


def _is_real_command(text: str, pattern: str) -> bool:
    """Check pattern appears as a real command, not in echo/printf/assignment."""
    for line in text.splitlines():
        if not re.search(pattern, line):
            continue
        trimmed = line.strip()
        # Reject echo, printf, no-ops, variable assignments
        if re.match(r"^(echo|printf|:|true|false)\b", trimmed):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", trimmed):
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both AMD CI scripts must be valid bash."""
    for script in SCRIPTS:
        r = subprocess.run(
            ["bash", "-n", script], capture_output=True, timeout=10
        )
        assert r.returncode == 0, (
            f"{script} has bash syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_exec_safe_directory():
    """Both scripts must have a real docker exec command setting safe.directory."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        assert _is_real_command(
            text, r"docker\s+exec\s+.*safe\.directory"
        ), f"{script}: no real docker exec setting safe.directory found"


# [pr_diff] fail_to_pass
def test_safe_directory_after_docker_run():
    """safe.directory config must appear AFTER docker run (container must exist first)."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        lines = text.splitlines()

        docker_run_line = None
        safe_dir_line = None
        for i, line in enumerate(lines):
            if re.search(r"docker\s+run\b", line):
                docker_run_line = i
            if re.search(r"safe\.directory", line):
                safe_dir_line = i

        assert docker_run_line is not None, f"{script}: no docker run found"
        assert safe_dir_line is not None, f"{script}: no safe.directory found"
        assert safe_dir_line > docker_run_line, (
            f"{script}: safe.directory (line {safe_dir_line}) must come after "
            f"docker run (line {docker_run_line})"
        )


# [pr_diff] fail_to_pass
def test_safe_directory_targets_checkout():
    """safe.directory must target /sglang-checkout or wildcard '*'."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        has_path = _is_real_command(text, r"safe\.directory.*/sglang-checkout")
        has_wildcard = _is_real_command(text, r"safe\.directory.*\*")
        assert has_path or has_wildcard, (
            f"{script}: safe.directory must target /sglang-checkout or '*'"
        )


# [pr_diff] fail_to_pass
def test_git_config_global_or_system():
    """git config must use --global or --system (bare git config only sets repo-local)."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        assert re.search(
            r"git\s+config\s+--(global|system)", text
        ), f"{script}: git config should use --global or --system flag"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_docker_run_preserved():
    """docker run --name ci_sglang must be preserved in both scripts."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        assert re.search(r"docker\s+run\b", text), (
            f"{script}: docker run command missing"
        )
        assert "--name ci_sglang" in Path(script).read_text(), (
            f"{script}: --name ci_sglang missing"
        )


# [pr_diff] pass_to_pass
def test_shebang_preserved():
    """Both scripts must retain a shebang line."""
    for script in SCRIPTS:
        first_line = Path(script).read_text().splitlines()[0]
        assert first_line.startswith("#!/"), (
            f"{script}: missing shebang (first line: {first_line!r})"
        )


# [pr_diff] fail_to_pass
def test_docker_exec_targets_ci_sglang():
    """docker exec must target the ci_sglang container (matches --name in docker run)."""
    for script in SCRIPTS:
        text = _read_no_comments(script)
        assert _is_real_command(
            text, r"docker\s+exec\s+.*ci_sglang.*safe\.directory"
        ), f"{script}: docker exec should target the ci_sglang container"
