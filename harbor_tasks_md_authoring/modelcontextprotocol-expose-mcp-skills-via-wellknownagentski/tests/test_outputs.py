"""Behavioral checks for modelcontextprotocol-expose-mcp-skills-via-wellknownagentski (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/modelcontextprotocol")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.mintlify/skills/search-mcp-github/SKILL.md')
    assert '../../../../plugins/mcp-spec/skills/search-mcp-github/SKILL.md' in text, "expected to find: " + '../../../../plugins/mcp-spec/skills/search-mcp-github/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/mcp-spec/skills/search-mcp-github/SKILL.md')
    assert 'license: Apache-2.0' in text, "expected to find: " + 'license: Apache-2.0'[:80]

