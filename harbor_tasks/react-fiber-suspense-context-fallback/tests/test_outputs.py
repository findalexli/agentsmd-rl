"""
Task: react-fiber-suspense-context-fallback
Repo: facebook/react @ f944b4c5352be02623d2d7415c0806350f875114

Fix: When propagating context changes through a Suspense boundary,
skip the primary (hidden) subtree and propagate into the fallback
subtree so its context consumers are marked for re-render.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberNewContext.js"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_primary_children_comment():
    """Fix should include explanatory comment about primary children's fibers."""
    src = Path(TARGET).read_text()
    assert "primary children" in src.lower() or "primaryChildFragment" in src, \
        "Should have comment or variable about primary children fibers"


def test_fallback_propagation():
    """Should propagate into fallback subtree via primaryChildFragment.sibling."""
    src = Path(TARGET).read_text()
    assert "primaryChildFragment" in src, \
        "Should reference primaryChildFragment to navigate to fallback"


def test_sibling_navigation():
    """Should use .sibling to reach fallback fragment."""
    src = Path(TARGET).read_text()
    # The fix sets nextFiber = primaryChildFragment.sibling
    assert ".sibling" in src and "primaryChildFragment" in src, \
        "Should navigate to fallback via primaryChildFragment.sibling"


def test_no_lazy_propagation_short_circuit():
    """Should not short-circuit with nextFiber = null for Suspense case."""
    src = Path(TARGET).read_text()
    # The old code had: if (!forcePropagateEntireTree) { nextFiber = null; }
    # The new code should skip the primary and go to fallback instead
    lines = src.split('\n')
    in_suspense_block = False
    for i, line in enumerate(lines):
        if 'primaryChildFragment' in line:
            in_suspense_block = True
        if in_suspense_block and 'sibling' in line:
            return  # Found the fix pattern
    assert False, "Could not find primaryChildFragment.sibling pattern"
