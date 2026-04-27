"""Behavioral checks for antigravity-awesome-skills-feat-add-laravelexpert-skill (markdown_authoring task).

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
    text = _read('skills/laravel-expert/SKILL.md')
    assert 'You follow modern Laravel standards and avoid legacy patterns unless explicitly required.' in text, "expected to find: " + 'You follow modern Laravel standards and avoid legacy patterns unless explicitly required.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-expert/SKILL.md')
    assert 'You provide production-grade, maintainable, and idiomatic Laravel solutions.' in text, "expected to find: " + 'You provide production-grade, maintainable, and idiomatic Laravel solutions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-expert/SKILL.md')
    assert '- Do not introduce microservice architecture unless requested' in text, "expected to find: " + '- Do not introduce microservice architecture unless requested'[:80]

