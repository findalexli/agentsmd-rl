"""
Task: vscode-chat-fork-progress
Repo: microsoft/vscode @ 99a7b4b0842dca767b056a303efa2412edfa16d8

Fix: Remove IProgressService dependency from chat fork actions and add
deduplication for concurrent fork operations via a pendingFork Map.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_progress_service_removed():
    """IProgressService import should be removed."""
    src = Path(TARGET).read_text()
    assert "IProgressService" not in src, \
        "IProgressService should be removed"


def test_pending_fork_map():
    """pendingFork Map should be defined for deduplication."""
    src = Path(TARGET).read_text()
    assert "pendingFork" in src, \
        "pendingFork Map should be defined"


def test_deduplication_logic():
    """Should check for pending fork before starting a new one."""
    src = Path(TARGET).read_text()
    assert "pendingFork.get" in src or "this.pendingFork" in src, \
        "Should check pendingFork map for existing operations"


def test_pending_fork_cleanup():
    """pendingFork entry should be deleted after completion."""
    src = Path(TARGET).read_text()
    assert "pendingFork.delete" in src, \
        "Should clean up pendingFork entry after completion"


def test_fork_method_on_action():
    """forkContributedChatSession should be a method on the action class."""
    src = Path(TARGET).read_text()
    assert "forkContributedChatSession" in src, \
        "forkContributedChatSession method should exist"


def test_no_progress_service_in_accessor():
    """accessor.get(IProgressService) should not be called."""
    src = Path(TARGET).read_text()
    assert "accessor.get(IProgressService)" not in src, \
        "Should not get IProgressService from accessor"
