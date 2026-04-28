"""Behavioral checks for agent-skills-fix-tlcspecdriven-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md')
    assert 'description: Project and feature planning with 4 phases - Specify, Design, Tasks, Implement+Validate. Creates atomic tasks with verification criteria and maintains persistent memory across sessions. S' in text, "expected to find: " + 'description: Project and feature planning with 4 phases - Specify, Design, Tasks, Implement+Validate. Creates atomic tasks with verification criteria and maintains persistent memory across sessions. S'[:80]

