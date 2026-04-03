"""
Task: vscode-chat-startover-action
Repo: microsoft/vscode @ d7ebb2cc7dcab5b7d7c9bc98ad5b96652dcab650

Fix: Add StartOverAction for first request checkpoint, add isFirstRequest
context key, and hide fork action on first request.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"


def test_start_over_action_registered():
    """StartOverAction should be registered in chatEditingActions.ts."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts").read_text()
    assert "StartOverAction" in src or "startOver" in src, \
        "StartOverAction should be defined"


def test_start_over_action_id():
    """StartOverAction should have correct action ID."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts").read_text()
    assert "workbench.action.chat.startOver" in src, \
        "StartOverAction should have id workbench.action.chat.startOver"


def test_is_first_request_context_key():
    """isFirstRequest context key should be defined in chatContextKeys.ts."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts").read_text()
    assert "isFirstRequest" in src, \
        "isFirstRequest context key should be defined"


def test_first_request_key_value():
    """isFirstRequest should use 'chatFirstRequest' as the key name."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts").read_text()
    assert "chatFirstRequest" in src, \
        "Context key should be named chatFirstRequest"


def test_fork_hidden_on_first_request():
    """Fork action should be hidden when isFirstRequest is true."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts").read_text()
    assert "isFirstRequest" in src, \
        "Fork action should reference isFirstRequest"


def test_is_first_request_bound_in_renderer():
    """isFirstRequest should be bound in chatListRenderer.ts."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts").read_text()
    assert "isFirstRequest" in src, \
        "isFirstRequest should be bound in renderer"


def test_start_over_shows_on_first_request():
    """StartOverAction should show only when isFirstRequest is true."""
    src = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts").read_text()
    assert "isFirstRequest" in src, \
        "StartOverAction menu should be conditioned on isFirstRequest"
