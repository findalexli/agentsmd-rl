"""Behavioral checks for courtlistener-docsclaudemd-add-ai-assistant-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/courtlistener")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Rules and guidance on our wiki is written with flexibility for humans, but MUST be strictly followed by AI agents. For example, if it says that something "should" be done, that\'s guidance to humans. A' in text, "expected to find: " + 'Rules and guidance on our wiki is written with flexibility for humans, but MUST be strictly followed by AI agents. For example, if it says that something "should" be done, that\'s guidance to humans. A'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When creating code that modify Django models, strictly follow the Database Migration guide: https://github.com/freelawproject/courtlistener/wiki/Database-migrations' in text, "expected to find: " + 'When creating code that modify Django models, strictly follow the Database Migration guide: https://github.com/freelawproject/courtlistener/wiki/Database-migrations'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read the testing guide before writing tests and follow it strictly: https://github.com/freelawproject/courtlistener/wiki/Automated-tests-on-CourtListener' in text, "expected to find: " + 'Read the testing guide before writing tests and follow it strictly: https://github.com/freelawproject/courtlistener/wiki/Automated-tests-on-CourtListener'[:80]

