"""Behavioral checks for buildwithclaude-add-tycana-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tycana/SKILL.md')
    assert 'Tycana gives Claude persistent memory about your work across conversations. Connect once via MCP, and every session includes your tasks, projects, deadlines, blockers, and computed intelligence from y' in text, "expected to find: " + 'Tycana gives Claude persistent memory about your work across conversations. Connect once via MCP, and every session includes your tasks, projects, deadlines, blockers, and computed intelligence from y'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tycana/SKILL.md')
    assert 'description: Persistent task management and productivity intelligence via MCP. Captures tasks from conversation, plans your day, tracks patterns, and gives personalized recommendations that improve ov' in text, "expected to find: " + 'description: Persistent task management and productivity intelligence via MCP. Captures tasks from conversation, plans your day, tracks patterns, and gives personalized recommendations that improve ov'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tycana/SKILL.md')
    assert "- **Capture from conversation** — mention something you need to do and it's captured with effort, energy, and project inferred from context" in text, "expected to find: " + "- **Capture from conversation** — mention something you need to do and it's captured with effort, energy, and project inferred from context"[:80]

