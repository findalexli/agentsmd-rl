"""Behavioral checks for ai-rules-builder-chore-create-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-rules-builder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'This is a web application that enables developers to quickly create so called "rules for AI" used by tools such as GitHub Copilot, Cursor and Windsurf, through an interactive, visual interface.' in text, "expected to find: " + 'This is a web application that enables developers to quickly create so called "rules for AI" used by tools such as GitHub Copilot, Cursor and Windsurf, through an interactive, visual interface.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- The ability to visually build AI rule sets representing different project aspects (architecture, technologies, coding conventions);' in text, "expected to find: " + '- The ability to visually build AI rule sets representing different project aspects (architecture, technologies, coding conventions);'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Support for various output formats compatible with popular AI tools (GitHub Copilot, Cursor, Claude);' in text, "expected to find: " + '- Support for various output formats compatible with popular AI tools (GitHub Copilot, Cursor, Claude);'[:80]

