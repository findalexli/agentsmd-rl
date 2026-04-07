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
