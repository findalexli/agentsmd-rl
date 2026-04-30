"""Behavioral checks for easy-dotnet.nvim-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/easy-dotnet.nvim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When working with Neovim-specific APIs (extmarks, `vim.ui`, floating windows, treesitter, etc.), **searching the internet is encouraged**. The Neovim docs and source are dense — community examples a' in text, "expected to find: " + '- When working with Neovim-specific APIs (extmarks, `vim.ui`, floating windows, treesitter, etc.), **searching the internet is encouraged**. The Neovim docs and source are dense — community examples a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'All intelligence, state, and business logic lives in the server (`easy-dotnet-server`). If you find yourself writing conditional logic about .NET concepts, project state, or build output in Lua — stop' in text, "expected to find: " + 'All intelligence, state, and business logic lives in the server (`easy-dotnet-server`). If you find yourself writing conditional logic about .NET concepts, project state, or build output in Lua — stop'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "> **If you are about to make changes that affect the JSON-RPC wire contract** (adding, removing, or changing any method name, parameter shape, or return type), you must read the server repo's instruct" in text, "expected to find: " + "> **If you are about to make changes that affect the JSON-RPC wire contract** (adding, removing, or changing any method name, parameter shape, or return type), you must read the server repo's instruct"[:80]

