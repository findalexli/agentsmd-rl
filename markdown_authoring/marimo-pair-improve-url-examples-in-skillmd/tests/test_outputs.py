"""Behavioral checks for marimo-pair-improve-url-examples-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marimo-pair")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| Execute code (by URL) | `bash scripts/execute-code.sh --url http://localhost:2718 -c "code"` | same (with `url` param) |' in text, "expected to find: " + '| Execute code (by URL) | `bash scripts/execute-code.sh --url http://localhost:2718 -c "code"` | same (with `url` param) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '# target a specific port (skips auto-selection when multiple servers run)' in text, "expected to find: " + '# target a specific port (skips auto-selection when multiple servers run)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "listings). If the server was started with `--mcp`, you'll have MCP tools" in text, "expected to find: " + "listings). If the server was started with `--mcp`, you'll have MCP tools"[:80]

