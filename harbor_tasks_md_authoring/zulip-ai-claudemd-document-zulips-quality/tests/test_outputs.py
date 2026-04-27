"""Behavioral checks for zulip-ai-claudemd-document-zulips-quality (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zulip")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'built to last for many years. It is developed by a vibrant open-source' in text, "expected to find: " + 'built to last for many years. It is developed by a vibrant open-source'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'making the codebase easy to understand and difficult to make dangerous' in text, "expected to find: " + 'making the codebase easy to understand and difficult to make dangerous'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- Think about edge cases in data: empty lists, very long names, single' in text, "expected to find: " + '- Think about edge cases in data: empty lists, very long names, single'[:80]

