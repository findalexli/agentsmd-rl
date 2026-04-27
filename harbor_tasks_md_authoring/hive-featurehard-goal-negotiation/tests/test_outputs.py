"""Behavioral checks for hive-featurehard-goal-negotiation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hive")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive-create/SKILL.md')
    assert '**If starting from a template and no modifications were made in Steps 2-5**, the nodes and edges are already registered. Skip to validation (`mcp__agent-builder__validate_graph()`). If modifications w' in text, "expected to find: " + '**If starting from a template and no modifications were made in Steps 2-5**, the nodes and edges are already registered. Skip to validation (`mcp__agent-builder__validate_graph()`). If modifications w'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive-create/SKILL.md')
    assert "**Communication sytle**: Be concise. Say less. Mean more. Impatient stakeholders don't want a wall of text — they want to know you get it. Every sentence you say should either move the conversation fo" in text, "expected to find: " + "**Communication sytle**: Be concise. Say less. Mean more. Impatient stakeholders don't want a wall of text — they want to know you get it. Every sentence you say should either move the conversation fo"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive-create/SKILL.md')
    assert 'description: Step-by-step guide for building goal-driven agents. Qualifies use cases first (the good, bad, and ugly), then creates package structure, defines goals, adds nodes, connects edges, and fin' in text, "expected to find: " + 'description: Step-by-step guide for building goal-driven agents. Qualifies use cases first (the good, bad, and ugly), then creates package structure, defines goals, adds nodes, connects edges, and fin'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert 'When this skill is loaded, **ALWAYS use the AskUserQuestion tool** to present options:' in text, "expected to find: " + 'When this skill is loaded, **ALWAYS use the AskUserQuestion tool** to present options:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert '- "Optimize agent design" → Then invoke /hive-patterns' in text, "expected to find: " + '- "Optimize agent design" → Then invoke /hive-patterns'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert '- "Set up credentials" → Then invoke /hive-credentials' in text, "expected to find: " + '- "Set up credentials" → Then invoke /hive-credentials'[:80]

