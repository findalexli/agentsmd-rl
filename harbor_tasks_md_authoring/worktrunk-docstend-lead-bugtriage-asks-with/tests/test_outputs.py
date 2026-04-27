"""Behavioral checks for worktrunk-docstend-lead-bugtriage-asks-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/worktrunk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'with this for unexplained failures rather than chaining version/config/repro' in text, "expected to find: " + 'with this for unexplained failures rather than chaining version/config/repro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert 'writes `.git/wt/logs/diagnostic.md` — a single report containing wt/git/OS' in text, "expected to find: " + 'writes `.git/wt/logs/diagnostic.md` — a single report containing wt/git/OS'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tend/SKILL.md')
    assert '- `wt config show` — when the suspicion is purely config/shell-integration' in text, "expected to find: " + '- `wt config show` — when the suspicion is purely config/shell-integration'[:80]

