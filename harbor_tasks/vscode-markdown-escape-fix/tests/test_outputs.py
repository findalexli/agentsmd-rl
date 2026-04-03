"""
Task: vscode-markdown-escape-fix
Repo: microsoft/vscode @ 33250873ecbd4047cd2e29b0f04ae0e7284aa342

Fix: Stop double-escaping markdown syntax in terminal run tool invocation
messages. The MarkdownString constructor already handles escaping, so
calling escapeMarkdownSyntaxTokens first causes double-escaping.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_escape_function_not_used():
    """escapeMarkdownSyntaxTokens should not be called on displayCommand."""
    src = Path(TARGET).read_text()
    assert "escapedDisplayCommand" not in src, \
        "escapedDisplayCommand variable should be removed"


def test_escape_import_removed():
    """escapeMarkdownSyntaxTokens should not be imported."""
    src = Path(TARGET).read_text()
    assert "escapeMarkdownSyntaxTokens" not in src, \
        "escapeMarkdownSyntaxTokens should be removed from imports"


def test_display_command_used_directly():
    """displayCommand should be passed directly to MarkdownString/localize."""
    src = Path(TARGET).read_text()
    # The fix passes displayCommand directly instead of escapedDisplayCommand
    assert "displayCommand)" in src or "displayCommand )" in src, \
        "displayCommand should be used directly in localize calls"


def test_markdown_string_still_used():
    """MarkdownString should still be used for invocation messages."""
    src = Path(TARGET).read_text()
    assert "new MarkdownString" in src, \
        "MarkdownString should still be used"
