"""Behavioral checks for opencontracts-updated-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencontracts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "5. Don't touch old tests without permission - if pre-existing tests fail after changes, try to identify why and present user with root cause analysis. If the test logic is correct but expectations nee" in text, "expected to find: " + "5. Don't touch old tests without permission - if pre-existing tests fail after changes, try to identify why and present user with root cause analysis. If the test logic is correct but expectations nee"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "1. No dead code - when deprecating or replacing code, always try to fully replace older code and, once it's no longer in use, delete it and related texts." in text, "expected to find: " + "1. No dead code - when deprecating or replacing code, always try to fully replace older code and, once it's no longer in use, delete it and related texts."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. Always ensure all affected (or new) tests pass - backend tests suite should only be run in its entirety for good reason as it takes 30+ minutes.' in text, "expected to find: " + '1. Always ensure all affected (or new) tests pass - backend tests suite should only be run in its entirety for good reason as it takes 30+ minutes.'[:80]

