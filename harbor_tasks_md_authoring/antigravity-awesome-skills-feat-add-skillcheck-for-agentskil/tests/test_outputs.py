"""Behavioral checks for antigravity-awesome-skills-feat-add-skillcheck-for-agentskil (markdown_authoring task).

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
    text = _read('skills/skill-check/SKILL.md')
    assert 'Validate SKILL.md files against the [agentskills specification](https://agentskills.io) and Anthropic best practices. Catches structural errors, semantic contradictions, naming anti-patterns, and qual' in text, "expected to find: " + 'Validate SKILL.md files against the [agentskills specification](https://agentskills.io) and Anthropic best practices. Catches structural errors, semantic contradictions, naming anti-patterns, and qual'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-check/SKILL.md')
    assert 'description: "Validate Claude Code skills against the agentskills specification. Catches structural, semantic, and naming issues before users do."' in text, "expected to find: " + 'description: "Validate Claude Code skills against the agentskills specification. Catches structural, semantic, and naming issues before users do."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-check/SKILL.md')
    assert 'Return structured results: score, grade (Excellent/Good/Needs Work/Poor), issue list with check IDs, line numbers, messages, and fix suggestions.' in text, "expected to find: " + 'Return structured results: score, grade (Excellent/Good/Needs Work/Poor), issue list with check IDs, line numbers, messages, and fix suggestions.'[:80]

