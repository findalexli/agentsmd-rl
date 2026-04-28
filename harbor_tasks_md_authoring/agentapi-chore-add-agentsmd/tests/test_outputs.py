"""Behavioral checks for agentapi-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentapi")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `lib/msgfmt/` - Message formatting for different agent types (claude, goose, aider, codex, gemini, amp, cursor-agent, cursor, auggie, custom)' in text, "expected to find: " + '- `lib/msgfmt/` - Message formatting for different agent types (claude, goose, aider, codex, gemini, amp, cursor-agent, cursor, auggie, custom)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a Go HTTP API server that controls coding agents (Claude Code, Aider, Goose, etc.) through terminal emulation.' in text, "expected to find: " + 'This is a Go HTTP API server that controls coding agents (Claude Code, Aider, Goose, etc.) through terminal emulation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `agentapi server --type=gemini -- gemini` - Start server with Gemini (requires explicit type)' in text, "expected to find: " + '- `agentapi server --type=gemini -- gemini` - Start server with Gemini (requires explicit type)'[:80]

