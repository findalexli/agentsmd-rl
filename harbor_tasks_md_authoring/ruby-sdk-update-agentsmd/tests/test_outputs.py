"""Behavioral checks for ruby-sdk-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruby-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Server registration**: `server.define_tool(name: "my_tool") { ... }`' in text, "expected to find: " + '3. **Server registration**: `server.define_tool(name: "my_tool") { ... }`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Dependencies: `json-schema` >= 4.1 - Schema validation' in text, "expected to find: " + '- Dependencies: `json-schema` >= 4.1 - Schema validation'[:80]

