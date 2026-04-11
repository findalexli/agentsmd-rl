"""
Task: wasp-refactor-build-commands-for-clarity
Repo: wasp-lang/wasp @ ed8f009c79766e66767307ea00fff365c9f12eae
PR:   3562

Rename build commands: build→build:hs, build:all→build, build:all:static→BUILD_STATIC env.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/wasp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / shell parse checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified shell scripts must parse without errors."""
    for script in ["waspc/run"]:
        r = subprocess.run(
            ["bash", "-n", script],
            cwd=REPO, capture_output=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"{script} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests on waspc/run
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_dispatches_all():
    """'build' command must dispatch to BUILD_ALL_CMD (packages + haskell)."""
    run_script = Path(REPO) / "waspc" / "run"
    content = run_script.read_text()

    # Find the case block for `build)` and verify it runs BUILD_ALL_CMD
    # The case statement pattern: build)\n    echo_and_eval "$BUILD_ALL_CMD"
    case_section = content[content.index("case $COMMAND in"):]
    build_match = re.search(
        r'^\s*build\)\s*\n\s*echo_and_eval\s+"\$BUILD_ALL_CMD"',
        case_section,
        re.MULTILINE,
    )
    assert build_match, (
        "'build)' case should dispatch to BUILD_ALL_CMD (packages + haskell), "
        "not BUILD_HS_CMD"
    )


# [pr_diff] fail_to_pass
def test_build_hs_command_exists():
    """'build:hs' command must exist in the run script."""
    run_script = Path(REPO) / "waspc" / "run"
    content = run_script.read_text()
    assert "build:hs)" in content, (
        "run script should have a 'build:hs' command for Haskell-only builds"
    )


# [pr_diff] fail_to_pass
def test_old_build_all_removed():
    """'build:all' and 'build:all:static' must not be case targets."""
    run_script = Path(REPO) / "waspc" / "run"
    content = run_script.read_text()
    case_section = content[content.index("case $COMMAND in"):]
    assert "build:all)" not in case_section, (
        "'build:all' case should be removed (renamed to 'build')"
    )
    assert "build:all:static)" not in case_section, (
        "'build:all:static' case should be removed"
    )


# [pr_diff] fail_to_pass
def test_static_via_env_var():
    """Static builds should be controlled via BUILD_STATIC env var, not a separate command."""
    run_script = Path(REPO) / "waspc" / "run"
    content = run_script.read_text()
    # BUILD_HS_CMD should incorporate BUILD_STATIC env var
    assert "BUILD_STATIC" in content, (
        "run script should use BUILD_STATIC env var for static builds"
    )
    # The old BUILD_ALL_STATIC_CMD should not exist
    assert "BUILD_ALL_STATIC_CMD" not in content, (
        "BUILD_ALL_STATIC_CMD should be removed in favor of BUILD_STATIC env var"
    )


# [pr_diff] fail_to_pass
def test_ci_uses_new_build_command():
    """CI workflow must use './run build' (not './run build:all')."""
    ci_file = Path(REPO) / ".github" / "workflows" / "ci-waspc-build.yaml"
    content = ci_file.read_text()
    assert "./run build\n" in content or "./run build\r\n" in content, (
        "CI should use './run build' as the build command"
    )
    assert "build:all" not in content, (
        "CI should not reference the old 'build:all' command"
    )


# [pr_diff] fail_to_pass
def test_powershell_build_dispatches_all():
    """PowerShell 'build' must dispatch to BUILD_ALL_CMD."""
    ps_script = Path(REPO) / "waspc" / "run.ps1"
    content = ps_script.read_text()
    # After "build" { should come BUILD_ALL_CMD, not BUILD_HS_CMD
    build_idx = content.index('"build"')
    # Get the next ~100 chars after the "build" match
    block = content[build_idx:build_idx + 150]
    assert "BUILD_ALL_CMD" in block, (
        "PowerShell 'build' case should invoke BUILD_ALL_CMD"
    )
    # build:hs should exist
    assert '"build:hs"' in content, (
        "PowerShell script should have a 'build:hs' command"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_packages_preserved():
    """'build:packages' command must still exist in the run script."""
    run_script = Path(REPO) / "waspc" / "run"
    content = run_script.read_text()
    assert "build:packages)" in content, (
        "'build:packages' command should not be removed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ci_file_valid_yaml():
    """The CI workflow file must exist and have valid structure (pass_to_pass)."""
    ci_file = Path(REPO) / ".github" / "workflows" / "ci-waspc-build.yaml"
    assert ci_file.exists(), "CI workflow file must exist"
    content = ci_file.read_text()
    # Check for basic YAML structure markers
    assert "name:" in content, "YAML must have a name field"
    assert "on:" in content or "true" in content.lower(), "YAML must have 'on' trigger section"
    assert "jobs:" in content, "YAML must have a jobs section"


# [repo_tests] pass_to_pass
def test_repo_run_script_bash_parse():
    """The waspc/run script must parse as valid bash (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", "waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"waspc/run has bash syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_run_script_version_cmd():
    """The waspc/run script get-waspc-version command works (pass_to_pass)."""
    r = subprocess.run(
        ["./run", "get-waspc-version"],
        cwd=f"{REPO}/waspc",
        capture_output=True, text=True, timeout=30,
    )
    # Note: cabal is not installed, but the script should still run and
    # either succeed or fail in a way that shows the script structure is valid
    # The important thing is the script parses and executes
    assert "cabal" in r.stderr or r.returncode == 0 or "waspc" in str(r.stdout), (
        f"get-waspc-version command should execute: stderr={r.stderr[:200]}"
    )


# [repo_tests] pass_to_pass
def test_repo_packages_compile_cmd_defined():
    """The WASP_PACKAGES_COMPILE command must be defined (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "grep -q 'WASP_PACKAGES_COMPILE=' waspc/run"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "WASP_PACKAGES_COMPILE must be defined in run script"
