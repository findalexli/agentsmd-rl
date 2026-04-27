"""Behavioral checks for gradio-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gradio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert "- **Don't use `toBeTruthy()` or `toBeFalsy()`.** These are too vague and hide intent. Use the most specific matcher for the value being checked:" in text, "expected to find: " + "- **Don't use `toBeTruthy()` or `toBeFalsy()`.** These are too vague and hide intent. Use the most specific matcher for the value being checked:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert '- Array non-empty → `toHaveLength(n)` or `expect(arr.length).toBeGreaterThan(0)`' in text, "expected to find: " + '- Array non-empty → `toHaveLength(n)` or `expect(arr.length).toBeGreaterThan(0)`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert '- Non-DOM null/undefined → `toBeNull()` / `toBeDefined()` / `toBeUndefined()`' in text, "expected to find: " + '- Non-DOM null/undefined → `toBeNull()` / `toBeDefined()` / `toBeUndefined()`'[:80]

