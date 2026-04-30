"""Behavioral checks for mcpspy-docsagents-add-claudemd-similar-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcpspy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '│   └── output/          # Output formatting (console, and file output)' in text, "expected to find: " + '│   └── output/          # Output formatting (console, and file output)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '|   |── http/            # HTTP transport parsing and analysis' in text, "expected to find: " + '|   |── http/            # HTTP transport parsing and analysis'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Focus on both stdio and HTTP transport (streamable HTTP).' in text, "expected to find: " + '- Focus on both stdio and HTTP transport (streamable HTTP).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'MCPSpy is a CLI utility that uses eBPF to monitor MCP (Model Context Protocol) communication by tracking stdio operations and analyzing JSON-RPC 2.0 messages.' in text, "expected to find: " + 'MCPSpy is a CLI utility that uses eBPF to monitor MCP (Model Context Protocol) communication by tracking stdio operations and analyzing JSON-RPC 2.0 messages.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Running all tests (unit tests, and end-to-end tests for both stdio and https transports):' in text, "expected to find: " + 'Running all tests (unit tests, and end-to-end tests for both stdio and https transports):'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '│   └── output/          # Output formatting (console, and file output)' in text, "expected to find: " + '│   └── output/          # Output formatting (console, and file output)'[:80]

