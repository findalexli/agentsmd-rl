"""Behavioral checks for scientific-agent-skills-add-bgpt-paper-search-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scientific-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-skills/bgpt-paper-search/SKILL.md')
    assert 'BGPT is a remote MCP server that searches a curated database of scientific papers built from raw experimental data extracted from full-text studies. Unlike traditional literature databases that return' in text, "expected to find: " + 'BGPT is a remote MCP server that searches a curated database of scientific papers built from raw experimental data extracted from full-text studies. Unlike traditional literature databases that return'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-skills/bgpt-paper-search/SKILL.md')
    assert 'description: Search scientific papers and retrieve structured experimental data extracted from full-text studies via the BGPT MCP server. Returns 25+ fields per paper including methods, results, sampl' in text, "expected to find: " + 'description: Search scientific papers and retrieve structured experimental data extracted from full-text studies via the BGPT MCP server. Returns 25+ fields per paper including methods, results, sampl'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-skills/bgpt-paper-search/SKILL.md')
    assert '- `literature-review` — Use BGPT to gather structured data, then synthesize with literature-review workflows' in text, "expected to find: " + '- `literature-review` — Use BGPT to gather structured data, then synthesize with literature-review workflows'[:80]

