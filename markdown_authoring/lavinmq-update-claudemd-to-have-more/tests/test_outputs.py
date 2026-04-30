"""Behavioral checks for lavinmq-update-claudemd-to-have-more (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lavinmq")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Performance** - Look for inefficient algorithms, unnecessary allocations, blocking operations' in text, "expected to find: " + '- **Performance** - Look for inefficient algorithms, unnecessary allocations, blocking operations'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Keep feedback under 200 words per file unless critical issues require detailed explanation' in text, "expected to find: " + '- Keep feedback under 200 words per file unless critical issues require detailed explanation'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **AMQP Compliance** - Ensure protocol implementations follow AMQP 0-9-1 specification' in text, "expected to find: " + '- **AMQP Compliance** - Ensure protocol implementations follow AMQP 0-9-1 specification'[:80]

