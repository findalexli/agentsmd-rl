"""
Task: vscode-sessions-contextkey-sync
Repo: microsoft/vscode @ 2924b6cf31bca9a2296af760209a088907def726

Fix: Synchronize IsWorkspaceGroupCappedContext key with persisted state
in SessionsView by binding and updating a workspaceGroupCappedContextKey.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_workspace_group_capped_context_key_field():
    """workspaceGroupCappedContextKey field should be defined on SessionsView."""
    src = Path(TARGET).read_text()
    assert "workspaceGroupCappedContextKey" in src, \
        "workspaceGroupCappedContextKey field should be defined"


def test_context_key_bound():
    """IsWorkspaceGroupCappedContext should be bound to contextKeyService."""
    src = Path(TARGET).read_text()
    assert "IsWorkspaceGroupCappedContext.bindTo" in src, \
        "IsWorkspaceGroupCappedContext should be bound"


def test_context_key_synced_in_render_body():
    """workspaceGroupCappedContextKey should be synced with persisted state."""
    src = Path(TARGET).read_text()
    assert "isWorkspaceGroupCapped()" in src, \
        "Should call isWorkspaceGroupCapped() to sync context key"


def test_context_key_set_on_reset():
    """workspaceGroupCappedContextKey should be set in the reset filter action."""
    src = Path(TARGET).read_text()
    # The key should be set in the reset action
    assert "workspaceGroupCappedContextKey?.set" in src or \
           "workspaceGroupCappedContextKey.set" in src, \
        "workspaceGroupCappedContextKey should be set"


def test_typed_as_boolean():
    """workspaceGroupCappedContextKey should be typed as IContextKey<boolean>."""
    src = Path(TARGET).read_text()
    assert "IContextKey<boolean>" in src, \
        "workspaceGroupCappedContextKey should be typed as IContextKey<boolean>"
