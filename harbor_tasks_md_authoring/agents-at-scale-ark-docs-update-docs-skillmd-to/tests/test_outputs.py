"""Behavioral checks for agents-at-scale-ark-docs-update-docs-skillmd-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents-at-scale-ark")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation/SKILL.md')
    assert '- Avoid gerunds: "Get started" not "Getting started," "Customize a layout" not "Customizing a layout".' in text, "expected to find: " + '- Avoid gerunds: "Get started" not "Getting started," "Customize a layout" not "Customizing a layout".'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation/SKILL.md')
    assert '- Don\'t use passive tense: "Complete the steps" not "The steps should be completed".' in text, "expected to find: " + '- Don\'t use passive tense: "Complete the steps" not "The steps should be completed".'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation/SKILL.md')
    assert '- Configure models, create agents, coordinate teams, run queries, add tools.' in text, "expected to find: " + '- Configure models, create agents, coordinate teams, run queries, add tools.'[:80]

