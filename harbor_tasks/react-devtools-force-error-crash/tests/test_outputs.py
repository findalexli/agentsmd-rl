"""
Task: react-devtools-force-error-crash
Repo: facebook/react @ 4610359651fa10247159e2050f8ec222cb7faa91
PR:   #35985

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary:
  shouldErrorFiberAccordingToMap in renderer.js returned `false` when a fiber
  had no entry in forceErrorForFibers (status === undefined).  Returning
  `false` caused updateClassComponent's switch to hit `case false:`, which
  tried to access workInProgress.stateNode on a class component that had
  never been constructed — crash.  The fix returns `null` instead so the
  switch hits `default:` (no-op), and updates the Flow return-type to
  `boolean | null`.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"
RECONCILER = f"{REPO}/packages/react-reconciler/src/ReactFiberBeginWork.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """Modified files exist and have content."""
    for f in [RENDERER, RECONCILER]:
        p = Path(f)
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 1000, f"{f} is suspiciously small"


# [static] pass_to_pass
def test_renderer_function_preserved():
    """shouldErrorFiberAccordingToMap function and core logic still exist."""
    # AST-only because: renderer.js uses Flow types inside a closure with thousands of deps
    content = Path(RENDERER).read_text()
    assert "shouldErrorFiberAccordingToMap" in content, (
        "Function shouldErrorFiberAccordingToMap not found in renderer.js"
    )
    assert "forceErrorForFibers" in content, (
        "forceErrorForFibers Map not found in renderer.js"
    )
    assert "status === undefined" in content, (
        "undefined status check not found in shouldErrorFiberAccordingToMap"
    )


# [static] pass_to_pass
def test_reconciler_switch_preserved():
    """switch on shouldError(workInProgress) and case false: still exist."""
    # AST-only because: ReactFiberBeginWork.js uses Flow types
    content = Path(RECONCILER).read_text()
    assert "shouldError(workInProgress)" in content, (
        "shouldError(workInProgress) call not found in reconciler"
    )
    # The case false: branch must still exist — it handles clearing errors
    # on components that HAVE been constructed
    assert "case false:" in content, (
        "case false: branch not found in shouldError switch"
    )


# [static] pass_to_pass
def test_renderer_returns_status_for_known_fibers():
    """Function still returns the actual status for known (mapped) fibers."""
    # AST-only because: renderer.js uses Flow types, closure-scoped
    content = Path(RENDERER).read_text()
    # After the undefined check, the function must still return the boolean status
    # for fibers that ARE in the map
    func_start = content.find("shouldErrorFiberAccordingToMap")
    assert func_start != -1
    func_region = content[func_start:func_start + 2000]
    assert "return status" in func_region, (
        "shouldErrorFiberAccordingToMap must still return status for known fibers"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_renderer_no_false_for_unknown_fiber():
    """shouldErrorFiberAccordingToMap must not return false when fiber has no entry.

    Returning false for unknown fibers caused the switch to hit `case false:`,
    which tried to access stateNode on a never-constructed class component.
    The fix returns null (or any non-boolean) so the switch hits default (no-op).
    """
    # AST-only because: renderer.js uses Flow types, closure-scoped function
    content = Path(RENDERER).read_text()

    idx = content.find("if (status === undefined)")
    assert idx != -1, "Could not find 'if (status === undefined)' in renderer.js"

    # The ~120 chars after the guard contain the return statement for this branch
    window = content[idx:idx + 120]
    assert "return false" not in window, (
        f"'return false' still present for undefined status — this causes the crash.\n"
        f"Context: {window!r}"
    )


# [pr_diff] fail_to_pass
def test_renderer_return_type_includes_null():
    """shouldErrorFiberAccordingToMap Flow return type must include null.

    The function can return null (unknown fiber), true (force error), or
    false (clear error).  The Flow type must reflect all three to catch
    callers that don't handle the null case.
    """
    # AST-only because: renderer.js uses Flow types
    content = Path(RENDERER).read_text()

    # Match the function signature with flexible whitespace
    pattern = r"shouldErrorFiberAccordingToMap\s*\([^)]*\)\s*:\s*([\w\s|]+?)\s*\{"
    match = re.search(pattern, content)
    assert match, "Could not find shouldErrorFiberAccordingToMap function signature"

    return_type = match.group(1).strip()
    assert "null" in return_type, (
        f"Return type is '{return_type}' but must include 'null' "
        f"(e.g., 'boolean | null')"
    )
