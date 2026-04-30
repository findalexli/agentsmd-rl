"""Behavioral checks for everything-claude-code-featskills-add-searchfirst-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/search-first/SKILL.md')
    assert 'description: Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Invokes the researcher agent.' in text, "expected to find: " + 'description: Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Invokes the researcher agent.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/search-first/SKILL.md')
    assert '| Exact match, well-maintained, MIT/Apache | **Adopt** — install and use directly |' in text, "expected to find: " + '| Exact match, well-maintained, MIT/Apache | **Adopt** — install and use directly |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/search-first/SKILL.md')
    assert '- **Ignoring MCP**: Not checking if an MCP server already provides the capability' in text, "expected to find: " + '- **Ignoring MCP**: Not checking if an MCP server already provides the capability'[:80]

