"""Behavioral checks for mcp-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Microsoft MCP (Model Context Protocol) servers provide AI agents with structured access to Azure, Microsoft Fabric, and other Microsoft services. This repository contains the core libraries, multiple ' in text, "expected to find: " + 'Microsoft MCP (Model Context Protocol) servers provide AI agents with structured access to Azure, Microsoft Fabric, and other Microsoft services. This repository contains the core libraries, multiple '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This documentation provides AI agents with comprehensive guidance for working effectively with the Microsoft MCP codebase. For additional details, see `/docs/new-command.md` for implementation specifi' in text, "expected to find: " + 'This documentation provides AI agents with comprehensive guidance for working effectively with the Microsoft MCP codebase. For additional details, see `/docs/new-command.md` for implementation specifi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **GitHub Copilot**: Install [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) and [GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub' in text, "expected to find: " + '2. **GitHub Copilot**: Install [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) and [GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub'[:80]

