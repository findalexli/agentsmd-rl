"""
Task: react-infinite-loop-warn-instead-of-throw
Repo: facebook/react @ 3f0b9e61c467cd6e09cac6fb69f6e8f68cd3c5d7

Fix: Distinguish between nested update kinds (sync lane vs phase spawn)
and warn via console.error instead of throwing for instrumentation-gated
infinite loop detection scenarios.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberWorkLoop.js"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_nested_update_kind_enum():
    """Should define nestedUpdateKind constants."""
    src = Path(TARGET).read_text()
    assert "NO_NESTED_UPDATE" in src, "Should define NO_NESTED_UPDATE constant"
    assert "NESTED_UPDATE_SYNC_LANE" in src, "Should define NESTED_UPDATE_SYNC_LANE constant"
    assert "NESTED_UPDATE_PHASE_SPAWN" in src, "Should define NESTED_UPDATE_PHASE_SPAWN constant"


def test_nested_update_kind_variable():
    """Should track nestedUpdateKind state variable."""
    src = Path(TARGET).read_text()
    assert "nestedUpdateKind" in src, "Should have nestedUpdateKind variable"


def test_warn_instead_of_throw_for_sync_lane():
    """For NESTED_UPDATE_SYNC_LANE in render context, should console.error not throw."""
    src = Path(TARGET).read_text()
    assert "NESTED_UPDATE_SYNC_LANE" in src, \
        "Should handle NESTED_UPDATE_SYNC_LANE case"
    # The fix uses console.error for the warn path
    assert "console.error" in src, \
        "Should use console.error for warning path"


def test_phase_spawn_warns():
    """NESTED_UPDATE_PHASE_SPAWN should also warn via console.error."""
    src = Path(TARGET).read_text()
    assert "NESTED_UPDATE_PHASE_SPAWN" in src, \
        "Should handle NESTED_UPDATE_PHASE_SPAWN case"


def test_update_kind_set_in_finish_work():
    """nestedUpdateKind should be set when detecting nested updates."""
    src = Path(TARGET).read_text()
    assert "nestedUpdateKind = NESTED_UPDATE_SYNC_LANE" in src, \
        "Should set nestedUpdateKind to NESTED_UPDATE_SYNC_LANE"
    assert "nestedUpdateKind = NESTED_UPDATE_PHASE_SPAWN" in src, \
        "Should set nestedUpdateKind to NESTED_UPDATE_PHASE_SPAWN"


def test_update_kind_reset():
    """nestedUpdateKind should be reset to NO_NESTED_UPDATE."""
    src = Path(TARGET).read_text()
    assert "nestedUpdateKind = NO_NESTED_UPDATE" in src, \
        "Should reset nestedUpdateKind to NO_NESTED_UPDATE"
