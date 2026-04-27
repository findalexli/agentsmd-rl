"""Behavioral checks for opc-skills-feat-add-amazon-platform-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opc-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert 'description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, GitHub, YouTube, LinkedIn, and Amazon. Use wh' in text, "expected to find: " + 'description: Generate user demand research reports from real user feedback. Scrape and analyze feature requests, complaints, and questions from Reddit, X, GitHub, YouTube, LinkedIn, and Amazon. Use wh'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert 'Generate user demand research reports by collecting and analyzing real user feedback from Reddit, X (Twitter), GitHub, YouTube, LinkedIn, and Amazon.' in text, "expected to find: " + 'Generate user demand research reports by collecting and analyzing real user feedback from Reddit, X (Twitter), GitHub, YouTube, LinkedIn, and Amazon.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert '| **Amazon** | Consumer products, electronics, home goods | Product review complaints and feature wishes | High for physical products |' in text, "expected to find: " + '| **Amazon** | Consumer products, electronics, home goods | Product review complaints and feature wishes | High for physical products |'[:80]

