"""Behavioral checks for marketingskills-fix-marketingideas-numbering-to-be (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/marketing-ideas/SKILL.md')
    assert 'description: "When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the user asks for \'marketing ideas,\' \'growth ideas,\' \'how to market,\' \'m' in text, "expected to find: " + 'description: "When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the user asks for \'marketing ideas,\' \'growth ideas,\' \'how to market,\' \'m'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/marketing-ideas/SKILL.md')
    assert 'You are a marketing strategist with a library of 139 proven marketing ideas. Your goal is to help users find the right marketing strategies for their specific situation, stage, and resources.' in text, "expected to find: " + 'You are a marketing strategist with a library of 139 proven marketing ideas. Your goal is to help users find the right marketing strategies for their specific situation, stage, and resources.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/marketing-ideas/SKILL.md')
    assert '- **free-tool-strategy**: For engineering as marketing (#15)' in text, "expected to find: " + '- **free-tool-strategy**: For engineering as marketing (#15)'[:80]

