"""Behavioral checks for codecompanion.nvim-chore-update-claudemd-and-agentsmd (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '- **Tools** (`interactions/chat/tools/builtin/`): `ask_questions`, `run_command`, `read_file`, `create_file`, `delete_file`, `insert_edit_into_file/`, `grep_search`, `file_search`, `web_search`, `fetc' in text, "expected to find: " + '- **Tools** (`interactions/chat/tools/builtin/`): `ask_questions`, `run_command`, `read_file`, `create_file`, `delete_file`, `insert_edit_into_file/`, `grep_search`, `file_search`, `web_search`, `fetc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a Neovim plugin written in Lua, which allows developers to code with LLMs and agents from within Neovim. Tests use Mini.Test with child processes. Always run the full test suite after changes ' in text, "expected to find: " + 'This is a Neovim plugin written in Lua, which allows developers to code with LLMs and agents from within Neovim. Tests use Mini.Test with child processes. Always run the full test suite after changes '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Don't over-explore the codebase with excessive grep/read calls. If you haven't converged on an approach after 3-4 searches, pause and share what you've found so far rather than continuing to search." in text, "expected to find: " + "- Don't over-explore the codebase with excessive grep/read calls. If you haven't converged on an approach after 3-4 searches, pause and share what you've found so far rather than continuing to search."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

