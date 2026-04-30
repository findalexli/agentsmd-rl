"""Behavioral checks for codecompanion.nvim-chore-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/codecompanion.nvim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Neovim plugin providing LLM-powered coding assistance with chat interface, inline code transformation, and extensible tools.' in text, "expected to find: " + 'Neovim plugin providing LLM-powered coding assistance with chat interface, inline code transformation, and extensible tools.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Keep functions under 50 lines, use descriptive names, and ensure all public APIs have type annotations.' in text, "expected to find: " + 'Keep functions under 50 lines, use descriptive names, and ensure all public APIs have type annotations.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Functions should describe their action (`should_include` not `include_ok`)' in text, "expected to find: " + '- Functions should describe their action (`should_include` not `include_ok`)'[:80]

