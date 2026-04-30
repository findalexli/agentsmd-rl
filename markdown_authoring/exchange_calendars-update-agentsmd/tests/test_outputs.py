"""Behavioral checks for exchange_calendars-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/exchange-calendars")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Expected sessions and times for each calendar are stored in a .csv file in @tests\\resources. During testing the contents of a .csv file are stored by an instance of the `Answers` class (of @tests\\test' in text, "expected to find: " + 'Expected sessions and times for each calendar are stored in a .csv file in @tests\\resources. During testing the contents of a .csv file are stored by an instance of the `Answers` class (of @tests\\test'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each calendar has a dedicated test file containing a dedicated test suite defined on a subclass of the common base class `ExchangeCalendarTestBase` (in @tests\\test_exchange_calendar.py).' in text, "expected to find: " + 'Each calendar has a dedicated test file containing a dedicated test suite defined on a subclass of the common base class `ExchangeCalendarTestBase` (in @tests\\test_exchange_calendar.py).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '├── etc/                                    # developer scripts and reference materials' in text, "expected to find: " + '├── etc/                                    # developer scripts and reference materials'[:80]

