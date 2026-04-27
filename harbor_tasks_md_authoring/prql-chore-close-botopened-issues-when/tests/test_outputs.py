"""Behavioral checks for prql-chore-close-botopened-issues-when (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'the fix has merged or the upstream problem has been addressed, close the issue' in text, "expected to find: " + 'the fix has merged or the upstream problem has been addressed, close the issue'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert "- Close bot-opened issues once the underlying cause is resolved — don't leave" in text, "expected to find: " + "- Close bot-opened issues once the underlying cause is resolved — don't leave"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'them open for a maintainer. If you (prql-bot) filed an issue (e.g., a nightly' in text, "expected to find: " + 'them open for a maintainer. If you (prql-bot) filed an issue (e.g., a nightly'[:80]

