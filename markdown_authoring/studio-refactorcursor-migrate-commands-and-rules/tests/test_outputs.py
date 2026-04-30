"""Behavioral checks for studio-refactorcursor-migrate-commands-and-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/add-mcp-tools/SKILL.md')
    assert 'description: Guide for adding new MCP tools with consistent patterns for schemas, tool definitions, registry updates, and Better Auth integration' in text, "expected to find: " + 'description: Guide for adding new MCP tools with consistent patterns for schemas, tool definitions, registry updates, and Better Auth integration'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/add-mcp-tools/SKILL.md')
    assert 'name: add-mcp-tools' in text, "expected to find: " + 'name: add-mcp-tools'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/commit/SKILL.md')
    assert 'description: Prepare code for review by running quality checks, creating conventional commits, and opening pull requests. Use when the user wants to commit changes, create a PR, prepare for code revie' in text, "expected to find: " + 'description: Prepare code for review by running quality checks, creating conventional commits, and opening pull requests. Use when the user wants to commit changes, create a PR, prepare for code revie'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/commit/SKILL.md')
    assert "If you're on the `main` branch, create a new feature branch first before making any commits." in text, "expected to find: " + "If you're on the `main` branch, create a new feature branch first before making any commits."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/commit/SKILL.md')
    assert 'Finally, report the GitHub PR URL.' in text, "expected to find: " + 'Finally, report the GitHub PR URL.'[:80]

