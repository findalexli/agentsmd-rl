"""Behavioral checks for finance-skills-shorten-skill-descriptions-to-fit (markdown_authoring task).

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
    text = _read('skills/funda-data/SKILL.md')
    assert 'analyst targets, DCF, options chain/flow/unusual activity, GEX, IV rank, max pain,' in text, "expected to find: " + 'analyst targets, DCF, options chain/flow/unusual activity, GEX, IV rank, max pain,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/funda-data/SKILL.md')
    assert 'analyst estimates, options flow/greeks/GEX, supply chain graph, social sentiment,' in text, "expected to find: " + 'analyst estimates, options flow/greeks/GEX, supply chain graph, social sentiment,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/funda-data/SKILL.md')
    assert 'Triggers: stock quotes, fundamentals, balance sheet, income statement, cash flow,' in text, "expected to find: " + 'Triggers: stock quotes, fundamentals, balance sheet, income statement, cash flow,'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert 'Use when the user asks about correlated stocks, related companies, sector peers,' in text, "expected to find: " + 'Use when the user asks about correlated stocks, related companies, sector peers,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert 'Also triggers for well-known pairs like AMD/NVDA, GOOGL/AVGO, LITE/COHR.' in text, "expected to find: " + 'Also triggers for well-known pairs like AMD/NVDA, GOOGL/AVGO, LITE/COHR.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert 'If only one ticker is provided, infer the user wants correlated peers.' in text, "expected to find: " + 'If only one ticker is provided, infer the user wants correlated peers.'[:80]

