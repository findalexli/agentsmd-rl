"""Behavioral checks for everything-claude-code-featskills-add-mcpserverpatterns (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mcp-server-patterns/SKILL.md')
    assert 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description' in text, "expected to find: " + 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mcp-server-patterns/SKILL.md')
    assert 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co' in text, "expected to find: " + 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mcp-server-patterns/SKILL.md')
    assert 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query ' in text, "expected to find: " + 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/mcp-server-patterns/SKILL.md')
    assert 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description' in text, "expected to find: " + 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/mcp-server-patterns/SKILL.md')
    assert 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co' in text, "expected to find: " + 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/mcp-server-patterns/SKILL.md')
    assert 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query ' in text, "expected to find: " + 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-server-patterns/SKILL.md')
    assert 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description' in text, "expected to find: " + 'Register tools and resources using the API your SDK version provides: some versions use `server.tool(name, description, schema, handler)` (positional args), others use `server.tool({ name, description'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-server-patterns/SKILL.md')
    assert 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co' in text, "expected to find: " + 'The Model Context Protocol (MCP) lets AI assistants call tools, read resources, and use prompts from your server. Use this skill when building or maintaining MCP servers. The SDK API evolves; check Co'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mcp-server-patterns/SKILL.md')
    assert 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query ' in text, "expected to find: " + 'For local clients, create a stdio transport and pass it to your server’s connect method. The exact API varies by SDK version (e.g. constructor vs factory). See the official MCP documentation or query '[:80]

