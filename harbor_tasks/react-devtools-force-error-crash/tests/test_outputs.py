"""
Task: react-devtools-force-error-crash
Repo: facebook/react @ 4610359651fa10247159e2050f8ec222cb7faa91

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary:
  shouldErrorFiberAccordingToMap in renderer.js was returning `false` when a
  fiber had no entry in forceErrorForFibers (status === undefined).  Returning
  `false` caused updateClassComponent to try to reset error-boundary state on
  an instance that had never been constructed, crashing.  The fix returns
  `null` instead, which the switch statement treats as "do nothing", and
  updates the Flow return-type annotation to `boolean | null`.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"
RECONCILER = f"{REPO}/packages/react-reconciler/src/ReactFiberBeginWork.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must parse without syntax errors."""
    for f in [RENDERER, RECONCILER]:
        r = subprocess.run(
            ["node", "--check", f],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"{f} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_storeForceError_regression():
    """storeForceError regression test passes — validates the crash fix end-to-end."""
    # This test file was added by the PR to reproduce the exact crash scenario:
    # forcing an error on a class component that has never been rendered before.
    test_file = Path(REPO) / "packages/react-devtools-shared/src/__tests__/storeForceError-test.js"
    assert test_file.exists(), (
        "storeForceError-test.js not found — PR patch not applied"
    )
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", "storeForceError"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"storeForceError test failed:\n{output[-3000:]}"


# [pr_diff] fail_to_pass
def test_renderer_null_return_for_unknown_fiber():
    """shouldErrorFiberAccordingToMap returns null (not false) when fiber has no forced-error entry.

    Returning false caused the reconciler to attempt resetting an error-boundary
    state on a class-component instance that had never been constructed, crashing.
    Returning null causes the switch to fall through to default (no-op).
    """
    # AST-only because: renderer.js uses Flow types and has thousands of deps
    # that cannot be executed standalone in Python.
    content = Path(RENDERER).read_text()

    # Locate the undefined-status guard
    idx = content.find("if (status === undefined)")
    assert idx != -1, "Could not find 'if (status === undefined)' in renderer.js"

    # The 50 chars after the guard should contain 'return null', not 'return false'
    window = content[idx : idx + 80]
    assert "return null" in window, (
        f"Expected 'return null' after 'if (status === undefined)', got:\n{window!r}"
    )
    assert "return false" not in window, (
        f"'return false' still present after 'if (status === undefined)':\n{window!r}"
    )


# [pr_diff] fail_to_pass
def test_renderer_flow_type_boolean_null():
    """shouldErrorFiberAccordingToMap Flow return type is 'boolean | null'.

    The old type 'boolean' was incorrect because the function can now return null,
    and an imprecise type would cause Flow to miss callers that don't handle null.
    """
    # AST-only because: renderer.js uses Flow types and can't execute standalone
    content = Path(RENDERER).read_text()

    assert "shouldErrorFiberAccordingToMap(fiber: any): boolean | null" in content, (
        "Function signature must have return type 'boolean | null' (not just 'boolean')"
    )
