"""Behavioral checks for obsidian-skills-add-instructions-about-json-newline (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/json-canvas/SKILL.md')
    assert 'In JSON, newline characters inside strings **must** be represented as `\\n`. Do **not** use the literal sequence `\\\\n` in a `.canvas` file—Obsidian will render it as the characters `\\` and `n` instead ' in text, "expected to find: " + 'In JSON, newline characters inside strings **must** be represented as `\\n`. Do **not** use the literal sequence `\\\\n` in a `.canvas` file—Obsidian will render it as the characters `\\` and `n` instead '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/json-canvas/SKILL.md')
    assert '{ "type": "text", "text": "Line 1\\\\nLine 2" }' in text, "expected to find: " + '{ "type": "text", "text": "Line 1\\\\nLine 2" }'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/json-canvas/SKILL.md')
    assert '{ "type": "text", "text": "Line 1\\nLine 2" }' in text, "expected to find: " + '{ "type": "text", "text": "Line 1\\nLine 2" }'[:80]

