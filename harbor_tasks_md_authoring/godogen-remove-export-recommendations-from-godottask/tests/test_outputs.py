"""Behavioral checks for godogen-remove-export-recommendations-from-godottask (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/godogen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/godot-task/SKILL.md')
    assert '**Script section ordering:** signals → @onready vars → private state → lifecycle methods → public methods → private methods → signal handlers' in text, "expected to find: " + '**Script section ordering:** signals → @onready vars → private state → lifecycle methods → public methods → private methods → signal handlers'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/godot-task/SKILL.md')
    assert 'var jump_velocity: float = -400.0' in text, "expected to find: " + 'var jump_velocity: float = -400.0'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/godot-task/SKILL.md')
    assert 'var move_force: float = 10.0' in text, "expected to find: " + 'var move_force: float = 10.0'[:80]

