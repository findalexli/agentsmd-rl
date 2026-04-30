"""Behavioral checks for obsidian-claude-pkm-add-search-skill-for-keyword (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-claude-pkm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/search/SKILL.md')
    assert 'description: Search vault content by keyword using Grep. Zero dependencies — works in any vault without indexes or plugins. Groups results by directory for easy scanning.' in text, "expected to find: " + 'description: Search vault content by keyword using Grep. Zero dependencies — works in any vault without indexes or plugins. Groups results by directory for easy scanning.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/search/SKILL.md')
    assert 'Fast keyword search across all vault markdown files using the Grep tool. No indexes, no plugins, no setup — just structured search with directory grouping.' in text, "expected to find: " + 'Fast keyword search across all vault markdown files using the Grep tool. No indexes, no plugins, no setup — just structured search with directory grouping.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/search/SKILL.md')
    assert 'After showing results, check if any matched files contain `[[wiki-links]]` to other notes. If so, briefly mention:' in text, "expected to find: " + 'After showing results, check if any matched files contain `[[wiki-links]]` to other notes. If so, briefly mention:'[:80]

