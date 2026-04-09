"""
Task: remix-feat-setup-installable-branch
Repo: remix-run/remix @ 598a92e3dc3488b02da7e4edafd1ff2498cc4c34
PR:   10964

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_pnpm_cmd(cmd, timeout=120):
    """Run a pnpm command with corepack enabled."""
    # Enable corepack first so pnpm is available
    subprocess.run(
        ["corepack", "enable"],
        capture_output=True, cwd=REPO, timeout=30
    )
    return subprocess.run(
        ["pnpm", cmd],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static / regression) — unchanged behavior must still work
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_getrootdir_still_works():
    """getRootDir (unchanged by PR) still returns cwd after logAndExec refactor."""
    result = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--input-type=module",
            "-e",
            "import { getRootDir } from './scripts/utils/process.ts';"
            "process.stdout.write(getRootDir())",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"getRootDir failed: {result.stderr}"
    assert result.stdout.strip() == REPO, f"Expected {REPO}, got: {result.stdout}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = _run_pnpm_cmd("lint", timeout=120)
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = _run_pnpm_cmd("typecheck", timeout=120)
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_changes_validate():
    """Repo's changes file validation passes (pass_to_pass)."""
    r = _run_pnpm_cmd("changes:validate", timeout=60)
    assert r.returncode == 0, f"Changes validate failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = _run_pnpm_cmd("format:check", timeout=60)
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = _run_pnpm_cmd("build", timeout=120)
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_logandexec_captures_output():
    """logAndExec with captureOutput=true returns captured command output."""
    result = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--input-type=module",
            "-e",
            "import { logAndExec } from './scripts/utils/process.ts';"
            "const out = logAndExec('echo captured_test_string', true);"
            "process.stdout.write('RESULT:' + out + ':END')",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"logAndExec capture failed: {result.stderr}"
    assert "RESULT:captured_test_string:END" in result.stdout, (
        f"Expected captured output between markers, got: {result.stdout}"
    )


# [pr_diff] fail_to_pass
def test_logandexec_default_returns_empty():
    """logAndExec with captureOutput=false (default) returns empty string."""
    result = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--input-type=module",
            "-e",
            "import { logAndExec } from './scripts/utils/process.ts';"
            "const out = logAndExec('echo hi');"
            "process.stdout.write('TYPE:' + typeof out + ':LEN:' + out.length)",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"logAndExec default failed: {result.stderr}"
    assert "TYPE:string:LEN:0" in result.stdout, (
        f"Expected empty string return, got: {result.stdout}"
    )


# [pr_diff] fail_to_pass
def test_setup_script_registered():
    """package.json must register setup-installable-branch as a runnable script."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "setup-installable-branch" in scripts, (
        "setup-installable-branch script missing from package.json"
    )
    script_val = scripts["setup-installable-branch"]
    assert "setup-installable-branch.ts" in script_val, (
        f"Script should reference setup-installable-branch.ts, got: {script_val}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config / documentation update tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_readme_has_installation_section():
    """README.md must document package installation and nightly builds."""
    readme = Path(f"{REPO}/README.md").read_text().lower()
    # Must describe how to install packages
    assert ("npm install" in readme or "pnpm install" in readme), (
        "README should document how to install packages"
    )
    # Must mention nightly builds for bleeding edge
    assert "nightly" in readme, "README should mention nightly builds"
    # Must mention pnpm for nightly install
    assert "pnpm" in readme, "README should document pnpm-based nightly install"


# [pr_diff] fail_to_pass
def test_contributing_has_nightly_builds():
    """CONTRIBUTING.md must document nightly build workflow and reference the setup script."""
    contributing = Path(f"{REPO}/CONTRIBUTING.md").read_text()
    lower = contributing.lower()
    # Must have a Nightly Builds section
    assert "nightly" in lower, "CONTRIBUTING.md should document nightly builds"
    # Must reference the setup script
    assert "setup-installable-branch" in contributing, (
        "CONTRIBUTING.md should reference the setup-installable-branch script"
    )
    # Must mention pnpm install command for nightly
    assert "pnpm install" in lower or "pnpm i " in lower, (
        "CONTRIBUTING.md should show how to install nightly builds"
    )
