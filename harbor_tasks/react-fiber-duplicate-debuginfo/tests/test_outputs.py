"""
Task: react-fiber-duplicate-debuginfo
Repo: facebook/react @ 272441a9ade6bf84de11ba73039eb4c80668fa6a
PR:   #35733

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: remove duplicate pushDebugInfo calls in reconcileChildFibersImpl for
isArray, getIteratorFn, and ASYNC_ITERATOR branches of ReactChildFiber.js.
When a Fragment is created for array/iterable children, the debug info is
already pushed during Fragment creation — pushing again in reconcileChildFibersImpl
causes duplicate debug info entries on child fibers.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = Path(f"{REPO}/packages/react-reconciler/src/ReactChildFiber.js")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_file_exists():
    """ReactChildFiber.js must exist at the expected path."""
    assert TARGET_FILE.exists(), f"Missing file: {TARGET_FILE}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — duplicate pushDebugInfo removed
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_array_branch_no_redundant_push():
    """isArray branch in reconcileChildFibersImpl must not call pushDebugInfo.

    Bug: when array children are processed in reconcileChildFibersImpl, pushDebugInfo
    was called again even though the Fragment fiber created one level up already pushed
    the debug info. This caused duplicate debug info entries on fiber children.
    Fix: remove `const prevDebugInfo = pushDebugInfo(...)` and
    `currentDebugInfo = prevDebugInfo` from the isArray branch.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()

    # Buggy pattern: pushDebugInfo called immediately after `if (isArray(newChild)) {`
    buggy = re.search(
        r'if \(isArray\(newChild\)\) \{\s*\n\s*const prevDebugInfo = pushDebugInfo',
        src,
    )
    assert buggy is None, (
        "isArray branch still calls pushDebugInfo — debug info from array children "
        "will be pushed twice onto the fiber debug stack"
    )


# [pr_diff] fail_to_pass
def test_iterator_branch_no_redundant_push():
    """getIteratorFn branch in reconcileChildFibersImpl must not call pushDebugInfo.

    Same duplicate-push bug as the isArray case: iterable children are wrapped in a
    Fragment that already pushed the debug info. Calling pushDebugInfo again inside
    reconcileChildFibersImpl creates duplicated debug info on child fibers.
    Fix: remove pushDebugInfo + currentDebugInfo = prevDebugInfo from this branch.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()

    buggy = re.search(
        r'if \(getIteratorFn\(newChild\)\) \{\s*\n\s*const prevDebugInfo = pushDebugInfo',
        src,
    )
    assert buggy is None, (
        "getIteratorFn branch still calls pushDebugInfo — debug info from iterable "
        "children will be pushed twice onto the fiber debug stack"
    )


# [pr_diff] fail_to_pass
def test_async_iterator_branch_no_redundant_push():
    """ASYNC_ITERATOR branch in reconcileChildFibersImpl must not call pushDebugInfo.

    Same duplicate-push bug for async iterables: the Fragment fiber already pushed
    the debug info. The async iterator branch must not call pushDebugInfo again.
    Fix: remove pushDebugInfo + currentDebugInfo = prevDebugInfo from this branch.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()

    # Find the async iterator conditional and check the block body
    async_iter_idx = src.find("typeof newChild[ASYNC_ITERATOR] === 'function'")
    assert async_iter_idx != -1, (
        "ASYNC_ITERATOR branch not found in ReactChildFiber.js"
    )

    # Get text from the condition to well past the block opening brace
    after_condition = src[async_iter_idx : async_iter_idx + 400]

    # Find ') {' that closes the if-condition and opens the block
    block_open = after_condition.find(') {')
    assert block_open != -1, "Could not find opening brace of ASYNC_ITERATOR block"

    # Check the first ~200 chars of the block body for pushDebugInfo
    block_content = after_condition[block_open + 3 : block_open + 200]
    assert 'pushDebugInfo' not in block_content, (
        "ASYNC_ITERATOR branch still calls pushDebugInfo — debug info from async "
        "iterable children will be pushed twice onto the fiber debug stack"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_fragment_creation_still_pushes_debug_info():
    """Fragment fiber creation must still call pushDebugInfo (not over-removed).

    The fix removes DUPLICATE pushDebugInfo calls in reconcileChildFibersImpl.
    The original call during Fragment fiber creation (near createFiberFromFragment)
    must remain — it is the single correct push that propagates debug info.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()

    frag_idx = src.find('createFiberFromFragment')
    assert frag_idx != -1, "createFiberFromFragment not found in ReactChildFiber.js"

    # pushDebugInfo must appear in a 500-char window around the Fragment creation call
    context = src[max(0, frag_idx - 400) : frag_idx + 200]
    assert 'pushDebugInfo' in context, (
        "pushDebugInfo not found near createFiberFromFragment — "
        "Fragment creation lost its debug info push (over-correction)"
    )


# [static] pass_to_pass
def test_array_branch_still_reconciles():
    """isArray branch must still call reconcileChildrenArray (not gutted).

    Verifies that the fix only removed the duplicate pushDebugInfo lines and
    did not accidentally remove the reconcileChildrenArray call itself.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()
    lines = src.split('\n')

    for i, line in enumerate(lines):
        if 'if (isArray(newChild))' in line:
            nearby = '\n'.join(lines[i : i + 10])
            assert 'reconcileChildrenArray' in nearby, (
                f"Line {i+1}: isArray branch no longer calls reconcileChildrenArray — "
                "the reconciliation logic was accidentally removed"
            )
            return

    assert False, "if (isArray(newChild)) not found in ReactChildFiber.js"


# [static] pass_to_pass
def test_reconcile_helpers_present():
    """All three reconciliation helpers must still be present in the file.

    Confirms the fix didn't gut reconcileChildrenArray, reconcileChildrenIteratable,
    or reconcileChildrenAsyncIteratable — each must still be defined/called.
    """
    # AST-only because: JavaScript file, cannot be imported in Python
    src = TARGET_FILE.read_text()

    for call in (
        'reconcileChildrenArray',
        'reconcileChildrenIteratable',
        'reconcileChildrenAsyncIteratable',
    ):
        assert call in src, (
            f"'{call}' not found in ReactChildFiber.js — "
            "reconciliation helper was accidentally removed"
        )
