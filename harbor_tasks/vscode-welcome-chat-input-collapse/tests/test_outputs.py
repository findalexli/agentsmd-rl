"""
Task: vscode-welcome-chat-input-collapse
Repo: microsoft/vscode @ abea71e2b7c1daecf68232d5d2a96efe3a6bc7f0

Fix: Set input part max height override before layout to prevent
chat widget from collapsing on the welcome page. Define named constants
for height values instead of magic numbers.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_set_input_part_max_height_override():
    """setInputPartMaxHeightOverride should be called before layout."""
    src = Path(TARGET).read_text()
    assert "setInputPartMaxHeightOverride" in src, \
        "Should call setInputPartMaxHeightOverride"


def test_layout_height_constant():
    """WELCOME_CHAT_INPUT_LAYOUT_HEIGHT constant should be defined."""
    src = Path(TARGET).read_text()
    assert "WELCOME_CHAT_INPUT_LAYOUT_HEIGHT" in src, \
        "WELCOME_CHAT_INPUT_LAYOUT_HEIGHT should be defined"


def test_reserved_list_height_constant():
    """WELCOME_CHAT_INPUT_RESERVED_LIST_HEIGHT constant should be defined."""
    src = Path(TARGET).read_text()
    assert "WELCOME_CHAT_INPUT_RESERVED_LIST_HEIGHT" in src, \
        "WELCOME_CHAT_INPUT_RESERVED_LIST_HEIGHT should be defined"


def test_reserved_chrome_height_constant():
    """WELCOME_CHAT_INPUT_RESERVED_CHROME_HEIGHT constant should be defined."""
    src = Path(TARGET).read_text()
    assert "WELCOME_CHAT_INPUT_RESERVED_CHROME_HEIGHT" in src, \
        "WELCOME_CHAT_INPUT_RESERVED_CHROME_HEIGHT should be defined"


def test_max_height_override_constant():
    """WELCOME_CHAT_INPUT_MAX_HEIGHT_OVERRIDE constant should be defined."""
    src = Path(TARGET).read_text()
    assert "WELCOME_CHAT_INPUT_MAX_HEIGHT_OVERRIDE" in src, \
        "WELCOME_CHAT_INPUT_MAX_HEIGHT_OVERRIDE should be defined"


def test_old_fixed_height_removed():
    """Old magic number 'const inputHeight = 150' should be removed."""
    src = Path(TARGET).read_text()
    assert "const inputHeight = 150" not in src, \
        "Old fixed inputHeight = 150 should be removed"


def test_layout_uses_named_constant():
    """layout() should use WELCOME_CHAT_INPUT_LAYOUT_HEIGHT, not literal."""
    src = Path(TARGET).read_text()
    assert "layout(WELCOME_CHAT_INPUT_LAYOUT_HEIGHT" in src, \
        "layout() should use named constant"
