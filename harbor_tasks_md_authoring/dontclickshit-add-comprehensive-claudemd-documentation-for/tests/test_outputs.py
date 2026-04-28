"""Behavioral checks for dontclickshit-add-comprehensive-claudemd-documentation-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dontclickshit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository contains a comprehensive personal cybersecurity guide aimed at helping regular users protect themselves from cyber threats. The guide\'s tagline "Don\'t click shit" (Ukrainian: "Не натис' in text, "expected to find: " + 'This repository contains a comprehensive personal cybersecurity guide aimed at helping regular users protect themselves from cyber threats. The guide\'s tagline "Don\'t click shit" (Ukrainian: "Не натис'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The guide is created by cybersecurity professionals with extensive experience in development, analysis, and ethical hacking of computer systems and networks. It provides practical, actionable advice f' in text, "expected to find: " + 'The guide is created by cybersecurity professionals with extensive experience in development, analysis, and ethical hacking of computer systems and networks. It provides practical, actionable advice f'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '8. **Contact Information**: Current contact is vlad@styran.com, with historical contact sapran@protonmail.com mentioned in some versions.' in text, "expected to find: " + '8. **Contact Information**: Current contact is vlad@styran.com, with historical contact sapran@protonmail.com mentioned in some versions.'[:80]

