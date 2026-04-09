"""
Task: react-offscreen-error-message
Repo: facebook/react @ cd515d7e22636238adef912356f522168946313d
PR:   35763

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = "packages/react-reconciler/src/getComponentNameFromFiber.js"
TEST_FILE = "packages/react-reconciler/src/__tests__/ReactIncrementalErrorLogging-test.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without JavaScript syntax errors."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/{TARGET_FILE}"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests + anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_offscreen_returns_parent_not_hardcoded():
    """
    OffscreenComponent case must return parent fiber name, not hardcoded 'Offscreen'.
    The fix changes the case from 'return "Offscreen"' to recursively
    calling getComponentNameFromFiber(fiber.return) to get the actual parent component.
    """
    src = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert "return 'Offscreen'" not in src, (
        "Function still returns hardcoded 'Offscreen' — fix not applied"
    )
    assert "getComponentNameFromFiber(fiber.return)" in src, (
        "Function must recursively walk to parent fiber via getComponentNameFromFiber(fiber.return)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_reconciler_tests():
    """React reconciler package tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn", "test",
            "packages/react-reconciler/src/__tests__/",
            "--no-watchman", "--silent",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"React reconciler tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_existing_error_logging_tests_pass():
    """Existing error logging tests must not break after the fix."""
    r = subprocess.run(
        [
            "yarn", "test", TEST_FILE,
            "--testNamePattern",
            "resets instance variables before unmounting failed node",
            "--no-watchman", "--silent",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Regression test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


