"""Behavioral checks for antigravity-awesome-skills-feat-add-nothumansearchmcp-and-ai (markdown_authoring task).

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
    text = _read('skills/ai-dev-jobs-mcp/SKILL.md')
    assert 'AI Dev Jobs is a remote MCP server that gives AI agents access to a live index of AI and ML job listings. As of April 17, 2026, the live MCP stats report 8,405 active roles across 489 companies, a $21' in text, "expected to find: " + 'AI Dev Jobs is a remote MCP server that gives AI agents access to a live index of AI and ML job listings. As of April 17, 2026, the live MCP stats report 8,405 active roles across 489 companies, a $21'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-dev-jobs-mcp/SKILL.md')
    assert 'description: "Search 8,400+ AI and ML jobs across 489 companies, inspect listings and employers, match roles, and view salary and market stats via AI Dev Jobs MCP"' in text, "expected to find: " + 'description: "Search 8,400+ AI and ML jobs across 489 companies, inspect listings and employers, match roles, and view salary and market stats via AI Dev Jobs MCP"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-dev-jobs-mcp/SKILL.md')
    assert 'Search the job index by keyword, location, company, or work arrangement. Returns matching listings with title, company, location, and salary information.' in text, "expected to find: " + 'Search the job index by keyword, location, company, or work arrangement. Returns matching listings with title, company, location, and salary information.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/not-human-search-mcp/SKILL.md')
    assert 'Not Human Search is a remote MCP server that lets AI agents search a curated index of 1,750+ AI-ready websites, inspect indexed site details, submit new sites for analysis, and verify live MCP endpoin' in text, "expected to find: " + 'Not Human Search is a remote MCP server that lets AI agents search a curated index of 1,750+ AI-ready websites, inspect indexed site details, submit new sites for analysis, and verify live MCP endpoin'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/not-human-search-mcp/SKILL.md')
    assert 'description: "Search AI-ready websites, inspect indexed site details, verify MCP endpoints, and discover tools and APIs using the Not Human Search MCP server"' in text, "expected to find: " + 'description: "Search AI-ready websites, inspect indexed site details, verify MCP endpoints, and discover tools and APIs using the Not Human Search MCP server"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/not-human-search-mcp/SKILL.md')
    assert 'The agent will call `search_agents({ query: "code review", limit: 10 })` and return ranked results with scores and endpoint details.' in text, "expected to find: " + 'The agent will call `search_agents({ query: "code review", limit: 10 })` and return ranked results with scores and endpoint details.'[:80]

