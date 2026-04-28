"""Behavioral checks for claude-code-game-studios-fix-missing-allowedtools-in-archite (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-game-studios")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/architecture-decision/SKILL.md')
    assert 'allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion' in text, "expected to find: " + 'allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/story-done/SKILL.md')
    assert 'allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion, Task' in text, "expected to find: " + 'allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion, Task'[:80]

