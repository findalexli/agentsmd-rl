"""Behavioral checks for dbhub-feat-add-agent-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dbhub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dbhub/SKILL.md')
    assert "description: Guide for querying databases through DBHub MCP server. Use this skill whenever you need to explore database schemas, inspect tables, or run SQL queries via DBHub's MCP tools (search_objec" in text, "expected to find: " + "description: Guide for querying databases through DBHub MCP server. Use this skill whenever you need to explore database schemas, inspect tables, or run SQL queries via DBHub's MCP tools (search_objec"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dbhub/SKILL.md')
    assert "When working with databases through DBHub's MCP server, always follow the **explore-then-query** pattern. Jumping straight to SQL without understanding the schema is the most common mistake — it leads" in text, "expected to find: " + "When working with databases through DBHub's MCP server, always follow the **explore-then-query** pattern. Jumping straight to SQL without understanding the schema is the most common mistake — it leads"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dbhub/SKILL.md')
    assert 'The `detail_level` parameter controls how much information `search_objects` returns. Start minimal and drill down only where needed — this keeps responses fast and token-efficient.' in text, "expected to find: " + 'The `detail_level` parameter controls how much information `search_objects` returns. Start minimal and drill down only where needed — this keeps responses fast and token-efficient.'[:80]

