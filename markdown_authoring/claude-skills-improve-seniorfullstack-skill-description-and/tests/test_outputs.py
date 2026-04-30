"""Behavioral checks for claude-skills-improve-seniorfullstack-skill-description-and (markdown_authoring task).

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
    text = _read('engineering-team/senior-fullstack/SKILL.md')
    assert 'stacks, runs static code quality analysis with security and complexity scoring,' in text, "expected to find: " + 'stacks, runs static code quality analysis with security and complexity scoring,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering-team/senior-fullstack/SKILL.md')
    assert 'Generates fullstack project boilerplate for Next.js, FastAPI, MERN, and Django' in text, "expected to find: " + 'Generates fullstack project boilerplate for Next.js, FastAPI, MERN, and Django'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering-team/senior-fullstack/SKILL.md')
    assert '1. Choose appropriate stack based on requirements (see Stack Decision Matrix)' in text, "expected to find: " + '1. Choose appropriate stack based on requirements (see Stack Decision Matrix)'[:80]

