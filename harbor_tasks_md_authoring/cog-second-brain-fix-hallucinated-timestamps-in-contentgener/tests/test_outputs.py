"""Behavioral checks for cog-second-brain-fix-hallucinated-timestamps-in-contentgener (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cog-second-brain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/braindump/SKILL.md')
    assert '2. Store this value and use it for ALL timestamp fields (`created:` frontmatter AND filename `HHMM` component)' in text, "expected to find: " + '2. Store this value and use it for ALL timestamp fields (`created:` frontmatter AND filename `HHMM` component)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/braindump/SKILL.md')
    assert '3. NEVER guess or fabricate the time — always use the value returned by the `date` command' in text, "expected to find: " + '3. NEVER guess or fabricate the time — always use the value returned by the `date` command'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/braindump/SKILL.md')
    assert "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time" in text, "expected to find: " + "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert '3. NEVER guess or fabricate the time — always use the value returned by the `date` command' in text, "expected to find: " + '3. NEVER guess or fabricate the time — always use the value returned by the `date` command'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time" in text, "expected to find: " + "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert '2. Store this value and use it for the `created:` frontmatter field' in text, "expected to find: " + '2. Store this value and use it for the `created:` frontmatter field'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/knowledge-consolidation/SKILL.md')
    assert '3. NEVER guess or fabricate the time — always use the value returned by the `date` command' in text, "expected to find: " + '3. NEVER guess or fabricate the time — always use the value returned by the `date` command'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/knowledge-consolidation/SKILL.md')
    assert "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time" in text, "expected to find: " + "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/knowledge-consolidation/SKILL.md')
    assert '2. Store this value and use it for the `created:` frontmatter field' in text, "expected to find: " + '2. Store this value and use it for the `created:` frontmatter field'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/weekly-checkin/SKILL.md')
    assert '3. NEVER guess or fabricate the time — always use the value returned by the `date` command' in text, "expected to find: " + '3. NEVER guess or fabricate the time — always use the value returned by the `date` command'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/weekly-checkin/SKILL.md')
    assert "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time" in text, "expected to find: " + "1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/weekly-checkin/SKILL.md')
    assert '2. Store this value and use it for the `created:` frontmatter field' in text, "expected to find: " + '2. Store this value and use it for the `created:` frontmatter field'[:80]

