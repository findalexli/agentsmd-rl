"""Behavioral checks for lucid-agents-claude-skills-for-agents-sdk (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lucid-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lucid-agents.skill.md')
    assert '- **Re-exports are banned** - Do not re-export types or values from other packages. Define types in `@lucid-agents/types` or in the package where they are used.' in text, "expected to find: " + '- **Re-exports are banned** - Do not re-export types or values from other packages. Define types in `@lucid-agents/types` or in the package where they are used.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lucid-agents.skill.md')
    assert 'One type definition per concept. Avoid duplicate types. Use type composition or generics, not separate type definitions.' in text, "expected to find: " + 'One type definition per concept. Avoid duplicate types. Use type composition or generics, not separate type definitions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lucid-agents.skill.md')
    assert 'Use this skill when working with the Lucid Agents SDK - a TypeScript framework for building and monetizing AI agents.' in text, "expected to find: " + 'Use this skill when working with the Lucid Agents SDK - a TypeScript framework for building and monetizing AI agents.'[:80]

