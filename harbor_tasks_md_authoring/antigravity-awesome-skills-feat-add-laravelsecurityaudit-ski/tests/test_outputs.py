"""Behavioral checks for antigravity-awesome-skills-feat-add-laravelsecurityaudit-ski (markdown_authoring task).

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
    text = _read('skills/laravel-security-audit/SKILL.md')
    assert "An authenticated user can access another user's resource by changing the ID." in text, "expected to find: " + "An authenticated user can access another user's resource by changing the ID."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-security-audit/SKILL.md')
    assert '- Do not recommend heavy external security packages unnecessarily' in text, "expected to find: " + '- Do not recommend heavy external security packages unnecessarily'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/laravel-security-audit/SKILL.md')
    assert 'The controller fetches a model by ID without verifying ownership.' in text, "expected to find: " + 'The controller fetches a model by ID without verifying ownership.'[:80]

