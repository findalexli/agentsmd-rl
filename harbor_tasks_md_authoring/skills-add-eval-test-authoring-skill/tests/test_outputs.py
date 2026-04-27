"""Behavioral checks for skills-add-eval-test-authoring-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill-test/SKILL.md')
    assert 'description: Scaffolds eval.yaml test files for agent skills in the dotnet/skills repository. Use when creating skill tests, writing evaluation scenarios, defining assertions and rubrics, or setting u' in text, "expected to find: " + 'description: Scaffolds eval.yaml test files for agent skills in the dotnet/skills repository. Use when creating skill tests, writing evaluation scenarios, defining assertions and rubrics, or setting u'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill-test/SKILL.md')
    assert 'Rubric items are evaluated by an LLM judge using pairwise comparison (baseline vs. skill-enhanced). Quality metrics (rubric-based at 40% weight plus overall judgment at 30%) together dominate the comp' in text, "expected to find: " + 'Rubric items are evaluated by an LLM judge using pairwise comparison (baseline vs. skill-enhanced). Quality metrics (rubric-based at 40% weight plus overall judgment at 30%) together dominate the comp'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill-test/SKILL.md')
    assert 'This skill helps you scaffold evaluation tests (`eval.yaml`) for agent skills, ensuring they conform to the dotnet/skills repository conventions, pass the skill-validator checks, and avoid common over' in text, "expected to find: " + 'This skill helps you scaffold evaluation tests (`eval.yaml`) for agent skills, ensuring they conform to the dotnet/skills repository conventions, pass the skill-validator checks, and avoid common over'[:80]

