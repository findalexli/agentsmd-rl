"""Behavioral checks for antigravity-awesome-skills-feat-add-viboscope-for-psychologi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/viboscope/SKILL.md')
    assert 'Viboscope helps find compatible people — cofounders, project partners, friends, romantic partners — through deep psychological compatibility matching. It builds a profile across 10 validated dimension' in text, "expected to find: " + 'Viboscope helps find compatible people — cofounders, project partners, friends, romantic partners — through deep psychological compatibility matching. It builds a profile across 10 validated dimension'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/viboscope/SKILL.md')
    assert 'Search across 7 contexts: business, romantic, friendship, professional, intellectual, hobby, general. Results include percentage scores and human-readable explanations of why you match.' in text, "expected to find: " + 'Search across 7 contexts: business, romantic, friendship, professional, intellectual, hobby, general. Results include percentage scores and human-readable explanations of why you match.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/viboscope/SKILL.md')
    assert 'The agent will guide you through profiling, then search for business-compatible matches with aligned values and complementary work styles.' in text, "expected to find: " + 'The agent will guide you through profiling, then search for business-compatible matches with aligned values and complementary work styles.'[:80]

