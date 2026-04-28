"""Behavioral checks for qtpass-docs-fix-qstringlistfilter-guidance-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert "When the goal is to drop env vars by name prefix, use `std::remove_if` with `startsWith`. Don't reach for `QStringList::filter()` — it does the opposite (keeps matching entries) and matches substrings" in text, "expected to find: " + "When the goal is to drop env vars by name prefix, use `std::remove_if` with `startsWith`. Don't reach for `QStringList::filter()` — it does the opposite (keeps matching entries) and matches substrings"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert '// Bad — filter() returns entries containing key, also matching "FOOBAR=value"' in text, "expected to find: " + '// Bad — filter() returns entries containing key, also matching "FOOBAR=value"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert '// when key is "FOO". And it selects, not removes; the assignment then drops' in text, "expected to find: " + '// when key is "FOO". And it selects, not removes; the assignment then drops'[:80]

