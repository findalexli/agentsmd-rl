"""
Task: vscode-chat-disposeelement-maps
Repo: microsoft/vscode @ cc967ecb5526e1e7e4fd5f4cc6e5be60f4947104

Fix: Clean up codeBlocksByResponseId, codeBlocksByEditorUri,
fileTreesByResponseId, and focusedFileTreesByResponseId maps when
chat list elements leave the viewport, preventing memory leaks.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_code_blocks_by_response_id_cleanup():
    """codeBlocksByResponseId should be cleaned up on element dispose."""
    src = Path(TARGET).read_text()
    assert "codeBlocksByResponseId.delete" in src, \
        "Should delete from codeBlocksByResponseId"


def test_code_blocks_by_editor_uri_cleanup():
    """codeBlocksByEditorUri should be cleaned up on element dispose."""
    src = Path(TARGET).read_text()
    assert "codeBlocksByEditorUri.delete" in src, \
        "Should delete from codeBlocksByEditorUri"


def test_file_trees_by_response_id_cleanup():
    """fileTreesByResponseId should be cleaned up on element dispose."""
    src = Path(TARGET).read_text()
    assert "fileTreesByResponseId.delete" in src, \
        "Should delete from fileTreesByResponseId"


def test_focused_file_trees_cleanup():
    """focusedFileTreesByResponseId should be cleaned up on element dispose."""
    src = Path(TARGET).read_text()
    assert "focusedFileTreesByResponseId.delete" in src, \
        "Should delete from focusedFileTreesByResponseId"


def test_cleanup_comment():
    """Should have explanatory comment about why cleanup is safe."""
    src = Path(TARGET).read_text()
    assert "focused response" in src.lower() or "always visible" in src.lower() or \
           "leave the viewport" in src.lower(), \
        "Should explain why cleanup is safe (focused response is always visible)"
