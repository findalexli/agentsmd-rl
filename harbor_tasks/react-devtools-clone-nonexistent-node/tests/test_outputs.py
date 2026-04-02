"""
Task: react-devtools-clone-nonexistent-node
Repo: facebook/react @ bb53387716e96912cbfb48d92655bc23882798ff

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = Path(REPO) / "packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """CommitTreeBuilder.js must be present in the workspace."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: existing error handling preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_fiber_collision_error_preserved():
    """'Commit tree already contains fiber' error must still be present (not removed)."""
    source = TARGET.read_text()
    assert "Commit tree already contains fiber" in source, (
        "Regression: existing fiber collision error was removed"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral checks
# AST-only because: getClonedNode is a closure inside updateTree with no exports;
# Flow type annotations prevent plain node execution; full React build required.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validates_node_existence_before_cloning():
    """getClonedNode must check that the node exists before cloning."""
    source = TARGET.read_text()
    assert "existingNode == null" in source or "existingNode === null" in source, (
        "Missing null/undefined check for existingNode before cloning"
    )


# [pr_diff] fail_to_pass
def test_throws_descriptive_error_for_missing_node():
    """getClonedNode must throw a descriptive error when the requested node is missing."""
    source = TARGET.read_text()
    assert "Could not clone the node" in source, (
        "Missing descriptive error throw for nonexistent node"
    )


# [pr_diff] fail_to_pass
def test_error_message_includes_fiber_id():
    """Error message must identify the missing fiber by its ID."""
    source = TARGET.read_text()
    # The gold patch uses a template literal: `...fiber "${id}"...`
    assert 'fiber "${id}"' in source, (
        "Error message does not include the fiber ID — agents cannot diagnose the root cause"
    )


# [pr_diff] fail_to_pass
def test_spread_operator_used_for_cloning():
    """Cloning must use object spread {...existingNode} instead of Object.assign."""
    source = TARGET.read_text()
    assert "{...existingNode}" in source, (
        "Spread operator {…existingNode} not found — Object.assign workaround not replaced"
    )
