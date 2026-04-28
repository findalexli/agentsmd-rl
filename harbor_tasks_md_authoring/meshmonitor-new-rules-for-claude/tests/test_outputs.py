"""Behavioral checks for meshmonitor-new-rules-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/meshmonitor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and ' in text, "expected to find: " + '- Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Default admin account is username 'admin' and password 'changeme' . Sometime the password is 'changeme1'" in text, "expected to find: " + "- Default admin account is username 'admin' and password 'changeme' . Sometime the password is 'changeme1'"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- use serena MCP for code search and analysis without me explicitly having to ask.' in text, "expected to find: " + '- use serena MCP for code search and analysis without me explicitly having to ask.'[:80]

