"""Behavioral checks for yfinance-mcp-docs-enhance-claudemd-with-detailed (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/yfinance-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Charts use WebP format for efficient token usage in MCP responses. The demo chatbot converts WebP to PNG for better browser compatibility. When adding new chart types, follow the pattern in `chart.py`' in text, "expected to find: " + 'Charts use WebP format for efficient token usage in MCP responses. The demo chatbot converts WebP to PNG for better browser compatibility. When adding new chart types, follow the pattern in `chart.py`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All MCP tool functions in `server.py` are async. Since `yfinance` is synchronous, all blocking calls are wrapped with `asyncio.to_thread()` to avoid blocking the event loop. This pattern should be mai' in text, "expected to find: " + 'All MCP tool functions in `server.py` are async. Since `yfinance` is synchronous, all blocking calls are wrapped with `asyncio.to_thread()` to avoid blocking the event loop. This pattern should be mai'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Use the `_error()` helper function to return consistent JSON error messages: `{"error": "message"}`. Always provide helpful error messages that guide users on how to fix the issue.' in text, "expected to find: " + 'Use the `_error()` helper function to return consistent JSON error messages: `{"error": "message"}`. Always provide helpful error messages that guide users on how to fix the issue.'[:80]

