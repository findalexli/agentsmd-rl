"""Behavioral checks for claude-code-design-skills-add-component-description-validati (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-design-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('figma-to-code/SKILL.md')
    assert '1. Display warning to user: "⚠️ Warning: Implementation may conflict with component guidelines: [specific conflict]"' in text, "expected to find: " + '1. Display warning to user: "⚠️ Warning: Implementation may conflict with component guidelines: [specific conflict]"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('figma-to-code/SKILL.md')
    assert '- If component has a `description` field, treat it as **authoritative usage guidelines**' in text, "expected to find: " + '- If component has a `description` field, treat it as **authoritative usage guidelines**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('figma-to-code/SKILL.md')
    assert '- **If implementing usage that conflicts with description guidelines:**' in text, "expected to find: " + '- **If implementing usage that conflicts with description guidelines:**'[:80]

