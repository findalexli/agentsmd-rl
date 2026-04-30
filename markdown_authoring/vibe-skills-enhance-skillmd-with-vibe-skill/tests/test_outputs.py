"""Behavioral checks for vibe-skills-enhance-skillmd-with-vibe-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**In OpenCode:** Use the `skill` tool. OpenCode natively supports skills from `.claude/skills/`, `.opencode/skills/`, and `.agents/skills/`. Invoke via `skill({ name: "skill-name" })`.' in text, "expected to find: " + '**In OpenCode:** Use the `skill` tool. OpenCode natively supports skills from `.claude/skills/`, `.opencode/skills/`, and `.agents/skills/`. Invoke via `skill({ name: "skill-name" })`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.' in text, "expected to find: " + '**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool." in text, "expected to find: " + "**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool."[:80]

