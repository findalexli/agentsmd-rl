"""Behavioral checks for publications-add-table-structure-guidelines-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/publications")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Every table row must have the same number of `|` delimiters as its header — no truncated or extra-long rows' in text, "expected to find: " + '- Every table row must have the same number of `|` delimiters as its header — no truncated or extra-long rows'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Do not leave rows truncated with missing columns — pad with empty cells (`| |`) if data is unavailable' in text, "expected to find: " + '- Do not leave rows truncated with missing columns — pad with empty cells (`| |`) if data is unavailable'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Security review tables use 5 columns: `| Product | Date | Effort | Announcement | Report |`' in text, "expected to find: " + '- Security review tables use 5 columns: `| Product | Date | Effort | Announcement | Report |`'[:80]

