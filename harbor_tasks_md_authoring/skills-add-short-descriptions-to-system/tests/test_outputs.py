"""Behavioral checks for skills-add-short-descriptions-to-system (markdown_authoring task).

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
    text = _read('skills/.system/plan/SKILL.md')
    assert 'short-description: Generate a plan for a complex task' in text, "expected to find: " + 'short-description: Generate a plan for a complex task'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.system/skill-creator/SKILL.md')
    assert 'The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing proc' in text, "expected to find: " + 'The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing proc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.system/skill-creator/SKILL.md')
    assert 'short-description: Create or update a skill' in text, "expected to find: " + 'short-description: Create or update a skill'[:80]

