"""Behavioral checks for csharp-sdk-set-up-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/csharp-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Follow the MCP specification at https://spec.modelcontextprotocol.io/ ([specification docs](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/main/docs/specification))' in text, "expected to find: " + '- Follow the MCP specification at https://spec.modelcontextprotocol.io/ ([specification docs](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/main/docs/specification))'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains the official C# SDK for the Model Context Protocol (MCP), enabling .NET applications to implement and interact with MCP clients and servers.' in text, "expected to find: " + 'This repository contains the official C# SDK for the Model Context Protocol (MCP), enabling .NET applications to implement and interact with MCP clients and servers.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `AIFunctionMcpServerTool`, `AIFunctionMcpServerPrompt`, and `AIFunctionMcpServerResource` wrap `AIFunction` for integration with Microsoft.Extensions.AI' in text, "expected to find: " + '- `AIFunctionMcpServerTool`, `AIFunctionMcpServerPrompt`, and `AIFunctionMcpServerResource` wrap `AIFunction` for integration with Microsoft.Extensions.AI'[:80]

