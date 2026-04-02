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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_suspense_offscreen_error_message():
    """Error thrown inside Suspense should report <Suspense>, not <Offscreen>."""
    r = subprocess.run(
        [
            "yarn", "test", TEST_FILE,
            "--testNamePattern",
            "does not report internal Offscreen component for errors thrown during reconciliation inside Suspense",
            "--no-watchman", "--silent",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Suspense error message test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_activity_offscreen_error_message():
    """Error thrown inside Activity should report <Activity>, not <Offscreen>."""
    r = subprocess.run(
        [
            "yarn", "test", TEST_FILE,
            "--testNamePattern",
            "does not report internal Offscreen component for errors thrown during reconciliation inside Activity",
            "--no-watchman", "--silent",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Activity error message test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

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


# [static] fail_to_pass
def test_not_stub():
    """OffscreenComponent case must walk up to parent, not return a hardcoded name."""
    # AST-only because: JavaScript file cannot be imported into Python
    src = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert "return 'Offscreen'" not in src, (
        "Function still returns hardcoded 'Offscreen' — fix not applied"
    )
    assert "getComponentNameFromFiber(fiber.return)" in src, (
        "Function must recursively walk to parent fiber via getComponentNameFromFiber(fiber.return)"
    )
