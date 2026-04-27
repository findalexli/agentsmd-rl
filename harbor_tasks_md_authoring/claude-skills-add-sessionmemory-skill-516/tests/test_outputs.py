"""Behavioral checks for claude-skills-add-sessionmemory-skill-516 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('session-memory/SKILL.md')
    assert 'description: Maintains a structured running-notes document during long work sessions. Use when the user says "session notes", "update notes", "start session notes", "show session notes", or when you r' in text, "expected to find: " + 'description: Maintains a structured running-notes document during long work sessions. Use when the user says "session notes", "update notes", "start session notes", "show session notes", or when you r'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('session-memory/SKILL.md')
    assert 'sections.** Update the *content* within sections; leave empty sections present' in text, "expected to find: " + 'sections.** Update the *content* within sections; leave empty sections present'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('session-memory/SKILL.md')
    assert '1. **Read the existing note** (if any) via `recall(tags_all=["session-memory",' in text, "expected to find: " + '1. **Read the existing note** (if any) via `recall(tags_all=["session-memory",'[:80]

