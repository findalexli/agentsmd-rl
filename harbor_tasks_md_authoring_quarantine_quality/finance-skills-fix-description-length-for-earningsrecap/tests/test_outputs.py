"""Behavioral checks for finance-skills-fix-description-length-for-earningsrecap (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/finance-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/earnings-recap/SKILL.md')
    assert 'Triggers: "AAPL earnings recap", "how did TSLA earnings go", "MSFT earnings results",' in text, "expected to find: " + 'Triggers: "AAPL earnings recap", "how did TSLA earnings go", "MSFT earnings results",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/earnings-recap/SKILL.md')
    assert '"earnings call recap", or any request about a company\'s recent earnings outcome.' in text, "expected to find: " + '"earnings call recap", or any request about a company\'s recent earnings outcome.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/earnings-recap/SKILL.md')
    assert 'understand beat/miss results, see stock reaction, or get an earnings recap.' in text, "expected to find: " + 'understand beat/miss results, see stock reaction, or get an earnings recap.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/estimate-analysis/SKILL.md')
    assert 'how EPS or revenue forecasts changed over time, compare estimate distributions,' in text, "expected to find: " + 'how EPS or revenue forecasts changed over time, compare estimate distributions,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/estimate-analysis/SKILL.md')
    assert 'Triggers: "estimate analysis for AAPL", "analyst estimate trends for NVDA",' in text, "expected to find: " + 'Triggers: "estimate analysis for AAPL", "analyst estimate trends for NVDA",'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/estimate-analysis/SKILL.md')
    assert 'Use this skill when the user asks about estimates beyond a simple lookup —' in text, "expected to find: " + 'Use this skill when the user asks about estimates beyond a simple lookup —'[:80]

