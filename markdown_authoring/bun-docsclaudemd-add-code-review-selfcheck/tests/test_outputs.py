"""Behavioral checks for bun-docsclaudemd-add-code-review-selfcheck (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bun")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Before writing code that makes a non-obvious choice, pre-emptively ask "why this and not the alternative?" If you can\'t answer, research until you can — don\'t write first and justify later.' in text, "expected to find: " + '- Before writing code that makes a non-obvious choice, pre-emptively ask "why this and not the alternative?" If you can\'t answer, research until you can — don\'t write first and justify later.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- If neighboring code does something differently than you're about to, find out _why_ before deviating — its choices are often load-bearing, not stylistic." in text, "expected to find: " + "- If neighboring code does something differently than you're about to, find out _why_ before deviating — its choices are often load-bearing, not stylistic."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Don't take a bug report's suggested fix at face value; verify it's the right layer." in text, "expected to find: " + "- Don't take a bug report's suggested fix at face value; verify it's the right layer."[:80]

