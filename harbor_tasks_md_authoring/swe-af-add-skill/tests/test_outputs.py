"""Behavioral checks for swe-af-add-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swe-af")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert 'SWE-AF creates a coordinated team of AI agents (planning, coding, review, QA, merge, verification) that execute in parallel based on DAG dependencies. Issues with no dependencies run simultaneously; d' in text, "expected to find: " + 'SWE-AF creates a coordinated team of AI agents (planning, coding, review, QA, merge, verification) that execute in parallel based on DAG dependencies. Issues with no dependencies run simultaneously; d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert 'Available roles: `pm`, `architect`, `tech_lead`, `sprint_planner`, `coder`, `qa`, `code_reviewer`, `qa_synthesizer`, `replan`, `retry_advisor`, `issue_writer`, `issue_advisor`, `verifier`, `git`, `mer' in text, "expected to find: " + 'Available roles: `pm`, `architect`, `tech_lead`, `sprint_planner`, `coder`, `qa`, `code_reviewer`, `qa_synthesizer`, `replan`, `retry_advisor`, `issue_writer`, `issue_advisor`, `verifier`, `git`, `mer'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert 'description: Autonomous engineering team runtime — one API call spins up coordinated AI agents to scope, build, and ship software.' in text, "expected to find: " + 'description: Autonomous engineering team runtime — one API call spins up coordinated AI agents to scope, build, and ship software.'[:80]

