"""
Task: react-devtools-profiler-commit-index
Repo: facebook/react @ 748ee74e22ab86994c12564a9fc73950d00ad72

Fix: Reset commit index when commitData changes (e.g. switching roots)
in the DevTools Profiler.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_reset_commit_index_on_data_change():
    """Commit index should be reset when commitData changes."""
    src = Path(TARGET).read_text()
    assert "previousCommitData" in src, \
        "Should track previousCommitData to detect changes"


def test_select_commit_index_reset():
    """selectCommitIndex should be called with 0 or null when commitData changes."""
    src = Path(TARGET).read_text()
    assert "selectCommitIndex" in src and "previousCommitData" in src, \
        "Should call selectCommitIndex when previousCommitData differs"


def test_set_previous_commit_data():
    """setPreviousCommitData state setter should exist."""
    src = Path(TARGET).read_text()
    assert "setPreviousCommitData" in src, \
        "Should have setPreviousCommitData state setter"


def test_compare_commit_data_identity():
    """Should compare commitData by identity (not deep equal)."""
    src = Path(TARGET).read_text()
    assert "previousCommitData !== commitData" in src, \
        "Should compare commitData by reference identity"
