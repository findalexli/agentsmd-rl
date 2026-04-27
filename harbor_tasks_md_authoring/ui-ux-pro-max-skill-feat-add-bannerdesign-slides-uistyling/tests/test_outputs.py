"""Behavioral checks for ui-ux-pro-max-skill-feat-add-bannerdesign-slides-uistyling (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ui-ux-pro-max-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-ux-pro-max/SKILL.md')
    assert '*For human/AI reference: follow priority 1→10 to decide which rule category to focus on first; use `--domain <Domain>` to query details when needed. Scripts do not read this table.*' in text, "expected to find: " + '*For human/AI reference: follow priority 1→10 to decide which rule category to focus on first; use `--domain <Domain>` to query details when needed. Scripts do not read this table.*'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-ux-pro-max/SKILL.md')
    assert 'This Skill should be used when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**.' in text, "expected to find: " + 'This Skill should be used when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ui-ux-pro-max/SKILL.md')
    assert '**Decision criteria**: If the task will change how a feature **looks, feels, moves, or is interacted with**, this Skill should be used.' in text, "expected to find: " + '**Decision criteria**: If the task will change how a feature **looks, feels, moves, or is interacted with**, this Skill should be used.'[:80]

