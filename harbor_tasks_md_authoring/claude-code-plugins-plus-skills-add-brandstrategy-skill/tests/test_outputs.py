"""Behavioral checks for claude-code-plugins-plus-skills-add-brandstrategy-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brand-strategy/SKILL.md')
    assert 'description: "A 7-part brand strategy framework for building comprehensive brand foundations. Use when users ask to: (1) Create or develop a brand strategy, (2) Build a brand brief or brand guidelines' in text, "expected to find: " + 'description: "A 7-part brand strategy framework for building comprehensive brand foundations. Use when users ask to: (1) Create or develop a brand strategy, (2) Build a brand brief or brand guidelines'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brand-strategy/SKILL.md')
    assert 'This skill guides users through a comprehensive brand strategy process, from core identity through measurement. Each phase builds on the previous, creating a cohesive strategic foundation.' in text, "expected to find: " + 'This skill guides users through a comprehensive brand strategy process, from core identity through measurement. Each phase builds on the previous, creating a cohesive strategic foundation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brand-strategy/SKILL.md')
    assert 'Walk the user through each phase sequentially. Ask discovery questions, synthesize their answers, and produce structured outputs for each section before moving to the next.' in text, "expected to find: " + 'Walk the user through each phase sequentially. Ask discovery questions, synthesize their answers, and produce structured outputs for each section before moving to the next.'[:80]

