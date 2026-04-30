"""Behavioral checks for content-improve-claude-skills-front-matter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/content")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/find-rule/SKILL.md')
    assert 'description: Search for existing rules that match a given requirement text. Identify rules that implement a specific control.' in text, "expected to find: " + 'description: Search for existing rules that match a given requirement text. Identify rules that implement a specific control.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/find-rule/SKILL.md')
    assert 'name: find-rule' in text, "expected to find: " + 'name: find-rule'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-profile/SKILL.md')
    assert 'description: Create or update a versioned profile pair (versioned + unversioned extends pattern).' in text, "expected to find: " + 'description: Create or update a versioned profile pair (versioned + unversioned extends pattern).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-profile/SKILL.md')
    assert 'name: manage-profile' in text, "expected to find: " + 'name: manage-profile'[:80]

