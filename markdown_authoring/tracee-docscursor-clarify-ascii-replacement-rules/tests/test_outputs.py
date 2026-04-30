"""Behavioral checks for tracee-docscursor-clarify-ascii-replacement-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tracee")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/shell-style-guide.mdc')
    assert '# BAD: No == in [ ] for max portability' in text, "expected to find: " + '# BAD: No == in [ ] for max portability'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/text-ascii-safety.mdc')
    assert '- arrows to `->` or the equivalent word (e.g., "returns", "maps to") depending on context' in text, "expected to find: " + '- arrows to `->` or the equivalent word (e.g., "returns", "maps to") depending on context'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/text-ascii-safety.mdc')
    assert "- curly single quotes to `'`" in text, "expected to find: " + "- curly single quotes to `'`"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/text-ascii-safety.mdc')
    assert '- curly double quotes to `"`' in text, "expected to find: " + '- curly double quotes to `"`'[:80]

