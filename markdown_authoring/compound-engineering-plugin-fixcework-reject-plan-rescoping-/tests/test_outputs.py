"""Behavioral checks for compound-engineering-plugin-fixcework-reject-plan-rescoping- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert "- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to" in text, "expected to find: " + "- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert "- If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority," in text, "expected to find: " + "- If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority,"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert "- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to" in text, "expected to find: " + "- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert "- If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority," in text, "expected to find: " + "- If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority,"[:80]

