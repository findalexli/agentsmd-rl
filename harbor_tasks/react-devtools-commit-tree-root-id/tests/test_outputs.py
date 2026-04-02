"""
Task: react-devtools-commit-tree-root-id
Repo: facebook/react @ 9a5996a6c144b4d6950b840f2098eff0117b5ac2
PR:   35710

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Structural checks are used throughout because the code under test is
JavaScript/Flow deeply integrated with React fiber internals — it cannot be
unit-tested in isolation without a full React browser environment.
"""

from pathlib import Path
import subprocess

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"
CONSTANTS = f"{REPO}/packages/react-devtools-shared/src/constants.js"
STORE = f"{REPO}/packages/react-devtools-shared/src/devtools/store.js"
COMMIT_TREE = f"{REPO}/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """renderer.js must pass Node.js syntax check."""
    # AST-only because: Flow syntax must be stripped to run; node --check validates JS/Flow grammar
    r = subprocess.run(
        ["node", "--check", RENDERER],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in renderer.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flush_pending_events_accepts_root_param():
    """flushPendingEvents must accept root: FiberInstance | null parameter."""
    # AST-only because: renderer.js is JavaScript/Flow with React fiber internals,
    # cannot be unit-tested in isolation.
    src = Path(RENDERER).read_text()
    assert "function flushPendingEvents(root: FiberInstance | null)" in src, \
        "flushPendingEvents must be defined as: function flushPendingEvents(root: FiberInstance | null)"


# [pr_diff] fail_to_pass
def test_brute_force_flush_accepts_root_param():
    """bruteForceFlushErrorsAndWarnings must accept root: FiberInstance parameter."""
    # AST-only because: renderer.js is JavaScript/Flow with React fiber internals,
    # cannot be unit-tested in isolation.
    src = Path(RENDERER).read_text()
    assert "function bruteForceFlushErrorsAndWarnings(root: FiberInstance)" in src, \
        "bruteForceFlushErrorsAndWarnings must accept root: FiberInstance parameter"


# [pr_diff] fail_to_pass
def test_flush_called_per_root_before_null():
    """flushPendingEvents(currentRoot) must appear just before currentRoot = (null: any)."""
    # AST-only because: execution requires full React fiber environment.
    # The bug: flushPendingEvents() was called once after all roots were processed,
    # by which point currentRoot was already null — losing the root context for the
    # commit tree builder. The fix calls flushPendingEvents(currentRoot) per-root
    # inside the forEach loop, before nulling currentRoot.
    src = Path(RENDERER).read_text()
    lines = src.splitlines()

    flush_lines = [i for i, l in enumerate(lines) if "flushPendingEvents(currentRoot)" in l]
    null_lines = [i for i, l in enumerate(lines) if "currentRoot = (null: any)" in l]

    assert flush_lines, "flushPendingEvents(currentRoot) not found in renderer.js"
    assert null_lines, "currentRoot = (null: any) not found in renderer.js"

    # At least one flushPendingEvents(currentRoot) must appear within 3 lines before a null assignment
    found = any(
        any(0 < (nl - fl) <= 3 for nl in null_lines)
        for fl in flush_lines
    )
    assert found, \
        "flushPendingEvents(currentRoot) must appear immediately before currentRoot = (null: any)"


# [pr_diff] fail_to_pass
def test_handle_post_commit_gets_root_instance():
    """handlePostCommitFiberRoot must retrieve rootInstance via rootToFiberInstanceMap."""
    # AST-only because: execution requires full React fiber environment.
    src = Path(RENDERER).read_text()
    assert "rootToFiberInstanceMap.get(root)" in src, \
        "handlePostCommitFiberRoot must call rootToFiberInstanceMap.get(root) to retrieve rootInstance"


# [pr_diff] fail_to_pass
def test_handle_post_commit_passes_root_to_flush():
    """handlePostCommitFiberRoot must call bruteForceFlushErrorsAndWarnings(rootInstance)."""
    # AST-only because: execution requires full React fiber environment.
    src = Path(RENDERER).read_text()
    assert "bruteForceFlushErrorsAndWarnings(rootInstance)" in src, \
        "bruteForceFlushErrorsAndWarnings must be called with rootInstance argument"


# [pr_diff] fail_to_pass
def test_flush_uses_root_id_not_current_root():
    """flushPendingEvents must use root.id (parameter) not currentRoot.id (stale closure)."""
    # AST-only because: static analysis of operations array construction.
    # The old code wrote currentRoot.id to the operations array, which was null
    # by the time flushPendingEvents ran after the forEach loop.
    src = Path(RENDERER).read_text()
    assert "operations[i++] = root.id" in src, \
        "flushPendingEvents must write root.id (parameter) into the operations array"
    assert "operations[i++] = currentRoot.id" not in src, \
        "flushPendingEvents must not reference currentRoot.id (stale closure variable)"


# [pr_diff] fail_to_pass
def test_handle_post_commit_fiber_root_flow_type():
    """handlePostCommitFiberRoot must use FiberRoot Flow type, not 'any'."""
    # AST-only because: static Flow type analysis.
    src = Path(RENDERER).read_text()
    assert "function handlePostCommitFiberRoot(root: FiberRoot)" in src, \
        "handlePostCommitFiberRoot must be typed as (root: FiberRoot), not (root: any)"


# [pr_diff] fail_to_pass
def test_tree_operation_remove_root_removed_from_constants():
    """TREE_OPERATION_REMOVE_ROOT must not be an active export in constants.js."""
    # AST-only because: static module analysis.
    src = Path(CONSTANTS).read_text()
    assert "export const TREE_OPERATION_REMOVE_ROOT" not in src, \
        "TREE_OPERATION_REMOVE_ROOT should not be an active export in constants.js"


# [pr_diff] fail_to_pass
def test_store_no_remove_root_case():
    """store.js must not contain a case for TREE_OPERATION_REMOVE_ROOT."""
    # AST-only because: static module analysis.
    src = Path(STORE).read_text()
    assert "case TREE_OPERATION_REMOVE_ROOT:" not in src, \
        "case TREE_OPERATION_REMOVE_ROOT should be removed from store.js"


# [pr_diff] fail_to_pass
def test_commit_tree_builder_no_remove_root():
    """CommitTreeBuilder.js must not reference TREE_OPERATION_REMOVE_ROOT at all."""
    # AST-only because: static module analysis.
    src = Path(COMMIT_TREE).read_text()
    assert "TREE_OPERATION_REMOVE_ROOT" not in src, \
        "CommitTreeBuilder.js should not import or handle TREE_OPERATION_REMOVE_ROOT"


# [pr_diff] fail_to_pass
def test_flush_pending_events_null_safe():
    """Non-tree-mutation flush paths must pass null explicitly, not omit the argument."""
    # AST-only because: static analysis of call sites.
    # After the fix, paths that don't involve tree mutations (e.g. error/warning updates,
    # filter changes) call flushPendingEvents(null) to make the intent explicit.
    src = Path(RENDERER).read_text()
    null_calls = src.count("flushPendingEvents(null)")
    assert null_calls >= 2, \
        f"Expected at least 2 flushPendingEvents(null) call sites, got {null_calls}"
