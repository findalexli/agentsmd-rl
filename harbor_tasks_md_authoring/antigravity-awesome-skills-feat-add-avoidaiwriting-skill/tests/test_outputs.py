"""Behavioral checks for antigravity-awesome-skills-feat-add-avoidaiwriting-skill (markdown_authoring task).

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
    text = _read('skills/avoid-ai-writing/SKILL.md')
    assert '**21 pattern categories:** formatting issues (em dashes, bold overuse, emoji headers, bullet-heavy sections), sentence structure problems (hedging, hollow intensifiers, rule of three), word/phrase rep' in text, "expected to find: " + '**21 pattern categories:** formatting issues (em dashes, bold overuse, emoji headers, bullet-heavy sections), sentence structure problems (hedging, hollow intensifiers, rule of three), word/phrase rep'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/avoid-ai-writing/SKILL.md')
    assert '"In today\'s rapidly evolving AI landscape, developers are embarking on a pivotal journey to leverage cutting-edge tools that streamline their workflows. Moreover, these robust solutions serve as a tes' in text, "expected to find: " + '"In today\'s rapidly evolving AI landscape, developers are embarking on a pivotal journey to leverage cutting-edge tools that streamline their workflows. Moreover, these robust solutions serve as a tes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/avoid-ai-writing/SKILL.md')
    assert 'Detects and fixes AI writing patterns ("AI-isms") that make text sound machine-generated. Covers 21 pattern categories with a 43-entry word/phrase replacement table that maps each flagged term to a sp' in text, "expected to find: " + 'Detects and fixes AI writing patterns ("AI-isms") that make text sound machine-generated. Covers 21 pattern categories with a 43-entry word/phrase replacement table that maps each flagged term to a sp'[:80]

