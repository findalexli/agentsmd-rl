"""Behavioral checks for fireworks-tech-graph-fix-invalid-yaml-frontmatter-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fireworks-tech-graph")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Use when the user wants to create any technical diagram - architecture, data' in text, "expected to find: " + 'Use when the user wants to create any technical diagram - architecture, data'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'flow, flowchart, sequence, agent/memory, or concept map - and export as' in text, "expected to find: " + 'flow, flowchart, sequence, agent/memory, or concept map - and export as'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '"可视化一下" "出图" "generate diagram" "draw diagram" "visualize" or any' in text, "expected to find: " + '"可视化一下" "出图" "generate diagram" "draw diagram" "visualize" or any'[:80]

