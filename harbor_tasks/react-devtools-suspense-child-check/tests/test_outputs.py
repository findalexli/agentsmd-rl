"""
Task: react-devtools-suspense-child-check
Repo: facebook/react @ 6066c782fe06b65e98a410741d994f620321fe11

Fix: When removing a suspense node, add an index === -1 guard before splice() to
prevent silent removal of the last child when the target ID is not found.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
STORE = "/workspace/react/packages/react-devtools-shared/src/devtools/store.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """store.js must be syntactically valid JavaScript."""
    r = subprocess.run(
        ["node", "--check", STORE],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in store.js:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_index_bounds_check_before_splice():
    """Must check index === -1 before calling splice in suspense remove block.

    On base: no guard → fails.
    After fix: guard present → passes.
    """
    src = Path(STORE).read_text()

    # Find the suspense remove block
    # The fix is: after `indexOf(id)`, check `if (index === -1)` before `splice`
    assert "const index = parentSuspense.children.indexOf(id);" in src, \
        "Expected indexOf call not found in store.js"

    # The guard must exist somewhere after the indexOf
    idx_of_pos = src.index("const index = parentSuspense.children.indexOf(id);")
    after_indexOf = src[idx_of_pos: idx_of_pos + 500]

    assert "index === -1" in after_indexOf, (
        "Missing bounds check: `if (index === -1)` must follow indexOf(id) "
        "before the splice call to prevent silent data corruption"
    )


# [pr_diff] fail_to_pass
def test_throw_and_emit_error_on_missing_child():
    """Must call _throwAndEmitError when the child ID is not found.

    On base: no error thrown → splice(-1) silently removes last child.
    After fix: _throwAndEmitError called with descriptive message.
    """
    src = Path(STORE).read_text()

    idx_of_pos = src.index("const index = parentSuspense.children.indexOf(id);")
    after_indexOf = src[idx_of_pos: idx_of_pos + 600]

    # Must use _throwAndEmitError (not console.error, not throw directly)
    assert "_throwAndEmitError" in after_indexOf, (
        "Fix must call `_throwAndEmitError` when index === -1, "
        "matching the existing error handling pattern in this function"
    )


# [pr_diff] fail_to_pass
def test_error_message_describes_parent_child_mismatch():
    """Error message must identify both the node and its intended parent.

    Checking 3 semantic signals in the error string to prevent a stub
    that just calls _throwAndEmitError(Error('')) or a trivial message.
    """
    src = Path(STORE).read_text()

    idx_of_pos = src.index("const index = parentSuspense.children.indexOf(id);")
    after_indexOf = src[idx_of_pos: idx_of_pos + 600]

    # The error message must convey the problem: cannot remove / not a child
    assert "Cannot remove suspense node" in after_indexOf or \
           "not a child" in after_indexOf or \
           "is not" in after_indexOf, \
        "Error message must describe that the node is not a child of the parent"

    # Must reference the parent concept
    assert "parent" in after_indexOf.lower(), \
        "Error message must reference the parent node"

    # Must use Error() constructor (not a string passed directly)
    assert "Error(" in after_indexOf, \
        "Must wrap error in Error() constructor for proper stack traces"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_dom_browser():
    """Repo's Flow type checking passes for dom-browser (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-browser"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_existing_error_patterns_preserved():
    """Other existing error checks in the suspense remove block must still be present.

    These guard other invariants; the fix must not disturb them.
    """
    src = Path(STORE).read_text()

    # Three known existing error messages in the same function
    existing = [
        "Cannot remove suspense node",     # existing OR new check (ok either way)
        "Cannot reorder children for suspense node",
        "Suspense children cannot be added or removed during a reorder",
    ]

    # At least two of the three must still exist (one may overlap with new check)
    found = sum(1 for msg in existing if msg in src)
    assert found >= 2, (
        f"Expected at least 2 of 3 existing error patterns to still be present, "
        f"found {found}. Patterns checked: {existing}"
    )


# [static] pass_to_pass
def test_splice_still_executed_on_valid_index():
    """The splice call must still exist (fix only guards it, doesn't remove it)."""
    src = Path(STORE).read_text()

    idx_of_pos = src.index("const index = parentSuspense.children.indexOf(id);")
    after_indexOf = src[idx_of_pos: idx_of_pos + 700]

    assert "parentSuspense.children.splice(index, 1)" in after_indexOf, \
        "The splice call must still be present after the guard check"
