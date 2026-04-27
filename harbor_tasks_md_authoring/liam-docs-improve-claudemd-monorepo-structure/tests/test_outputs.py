"""Behavioral checks for liam-docs-improve-claudemd-monorepo-structure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/liam")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **frontend/internal-packages/mcp-server** - MCP server implementation (`@liam-hq/mcp-server`)' in text, "expected to find: " + '- **frontend/internal-packages/mcp-server** - MCP server implementation (`@liam-hq/mcp-server`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **frontend/internal-packages/agent** - AI agent system using LangGraph (`@liam-hq/agent`)' in text, "expected to find: " + '- **frontend/internal-packages/agent** - AI agent system using LangGraph (`@liam-hq/agent`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **frontend/internal-packages/db** - Database utilities (`@liam-hq/db`)' in text, "expected to find: " + '- **frontend/internal-packages/db** - Database utilities (`@liam-hq/db`)'[:80]

