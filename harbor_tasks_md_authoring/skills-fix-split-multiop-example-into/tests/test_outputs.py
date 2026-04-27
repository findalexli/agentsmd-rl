"""Behavioral checks for skills-fix-split-multiop-example-into (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-mcp-server/SKILL.md')
    assert 'Each file must contain exactly one operation. Each named operation becomes an MCP tool.' in text, "expected to find: " + 'Each file must contain exactly one operation. Each named operation becomes an MCP tool.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-mcp-server/SKILL.md')
    assert '# operations/CreateUser.graphql' in text, "expected to find: " + '# operations/CreateUser.graphql'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-mcp-server/SKILL.md')
    assert '# operations/GetUser.graphql' in text, "expected to find: " + '# operations/GetUser.graphql'[:80]

