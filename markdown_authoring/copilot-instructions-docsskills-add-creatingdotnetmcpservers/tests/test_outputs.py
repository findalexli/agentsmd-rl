"""Behavioral checks for copilot-instructions-docsskills-add-creatingdotnetmcpservers (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-instructions")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/SKILL.md')
    assert 'description: Use when building Model Context Protocol (MCP) servers in .NET, configuring tools, transports (SSE/stdio), JSON serialization for AOT, or testing MCP endpoints' in text, "expected to find: " + 'description: Use when building Model Context Protocol (MCP) servers in .NET, configuring tools, transports (SSE/stdio), JSON serialization for AOT, or testing MCP endpoints'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/SKILL.md')
    assert '**Core principle:** MCP servers expose tools via standardized protocol using attribute-based registration and explicit JSON serialization contexts for AOT.' in text, "expected to find: " + '**Core principle:** MCP servers expose tools via standardized protocol using attribute-based registration and explicit JSON serialization contexts for AOT.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/SKILL.md')
    assert '**Key patterns:** Sealed classes, const tool names, `[Description]` on method and parameters, always accept `CancellationToken`.' in text, "expected to find: " + '**Key patterns:** Sealed classes, const tool names, `[Description]` on method and parameters, always accept `CancellationToken`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/advanced.md')
    assert 'public PackageTools(IQueryHandler<SearchPackagesQuery, IEnumerable<PackageMetadata>> searchHandler) { }' in text, "expected to find: " + 'public PackageTools(IQueryHandler<SearchPackagesQuery, IEnumerable<PackageMetadata>> searchHandler) { }'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/advanced.md')
    assert '.WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")' in text, "expected to find: " + '.WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/advanced.md')
    assert 'Clean Architecture integration, configuration patterns, and production deployment for MCP servers.' in text, "expected to find: " + 'Clean Architecture integration, configuration patterns, and production deployment for MCP servers.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/error-handling.md')
    assert '**Never throw unhandled exceptions** - MCP tools should return structured error responses instead of letting exceptions bubble up. This provides better UX for LLM clients and makes debugging easier.' in text, "expected to find: " + '**Never throw unhandled exceptions** - MCP tools should return structured error responses instead of letting exceptions bubble up. This provides better UX for LLM clients and makes debugging easier.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/error-handling.md')
    assert 'Best practices for handling errors gracefully in MCP tools and returning meaningful messages to clients.' in text, "expected to find: " + 'Best practices for handling errors gracefully in MCP tools and returning meaningful messages to clients.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/error-handling.md')
    assert '_logger.LogError(ex, "Unexpected error during package search for query: {Query}", query);' in text, "expected to find: " + '_logger.LogError(ex, "Unexpected error during package search for query: {Query}", query);'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/testing.md')
    assert "| No `WebApplicationFactory` in integration tests | Can't test real transport → Use factory pattern |" in text, "expected to find: " + "| No `WebApplicationFactory` in integration tests | Can't test real transport → Use factory pattern |"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/testing.md')
    assert 'Complete guide for testing MCP tools with integration tests, unit tests, and test patterns.' in text, "expected to find: " + 'Complete guide for testing MCP tools with integration tests, unit tests, and test patterns.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/creating-dotnet-mcp-servers/references/testing.md')
    assert '| Port conflicts in parallel tests | Use unique ports per test or dynamic port allocation |' in text, "expected to find: " + '| Port conflicts in parallel tests | Use unique ports per test or dynamic port allocation |'[:80]

