"""Behavioral checks for antigravity-awesome-skills-feat-add-manageskills-for-crossto (markdown_authoring task).

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
    text = _read('skills/manage-skills/SKILL.md')
    assert 'description: Discover, list, create, edit, toggle, copy, move, and delete AI agent skills across 11 tools (Cursor, Claude, Agents, Windsurf, Copilot, Codex, Cline, Aider, Continue, Roo Code, Augment)' in text, "expected to find: " + 'description: Discover, list, create, edit, toggle, copy, move, and delete AI agent skills across 11 tools (Cursor, Claude, Agents, Windsurf, Copilot, Codex, Cline, Aider, Continue, Roo Code, Augment)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/manage-skills/SKILL.md')
    assert 'You can manage skills and rules for all major AI coding tools directly from the terminal. This skill teaches you the directory layout, file format, and operations for each tool.' in text, "expected to find: " + 'You can manage skills and rules for all major AI coding tools directly from the terminal. This skill teaches you the directory layout, file format, and operations for each tool.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/manage-skills/SKILL.md')
    assert 'Plugin skills are cached at `~/.cursor/plugins/cache/<org>/<plugin>/<version>/skills/<name>/SKILL.md`. These are managed by Cursor and should not be edited directly.' in text, "expected to find: " + 'Plugin skills are cached at `~/.cursor/plugins/cache/<org>/<plugin>/<version>/skills/<name>/SKILL.md`. These are managed by Cursor and should not be edited directly.'[:80]

