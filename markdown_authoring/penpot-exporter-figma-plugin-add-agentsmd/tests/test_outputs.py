"""Behavioral checks for penpot-exporter-figma-plugin-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/penpot-exporter-figma-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Penpot Exporter** is a Figma plugin that converts Figma files into `.zip` packages importable by' in text, "expected to find: " + '**Penpot Exporter** is a Figma plugin that converts Figma files into `.zip` packages importable by'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Penpot common types](https://github.com/penpot/penpot/tree/develop/common/src/app/common/types)' in text, "expected to find: " + '- [Penpot common types](https://github.com/penpot/penpot/tree/develop/common/src/app/common/types)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "[Penpot](https://penpot.app/). The plugin traverses Figma's node tree, transforms each node into" in text, "expected to find: " + "[Penpot](https://penpot.app/). The plugin traverses Figma's node tree, transforms each node into"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

