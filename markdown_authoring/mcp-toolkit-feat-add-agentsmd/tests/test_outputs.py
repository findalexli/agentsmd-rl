"""Behavioral checks for mcp-toolkit-feat-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Nuxt MCP Toolkit** is a Nuxt module that enables developers to create [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers directly in their Nuxt applications. It provides automat' in text, "expected to find: " + '**Nuxt MCP Toolkit** is a Nuxt module that enables developers to create [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers directly in their Nuxt applications. It provides automat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The module includes a built-in inspector in Nuxt DevTools for debugging MCP definitions. Access it via the DevTools panel when running in development mode.' in text, "expected to find: " + 'The module includes a built-in inspector in Nuxt DevTools for debugging MCP definitions. Access it via the DevTools panel when running in development mode.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This module uses `@modelcontextprotocol/sdk` version 1.23.0+. When referencing SDK documentation, ensure compatibility with this version.' in text, "expected to find: " + 'This module uses `@modelcontextprotocol/sdk` version 1.23.0+. When referencing SDK documentation, ensure compatibility with this version.'[:80]

