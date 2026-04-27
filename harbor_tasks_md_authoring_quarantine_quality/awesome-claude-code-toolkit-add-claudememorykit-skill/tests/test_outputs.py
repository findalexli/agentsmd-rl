"""Behavioral checks for awesome-claude-code-toolkit-add-claudememorykit-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-memory-kit/SKILL.md')
    assert 'description: "Persistent memory system for Claude Code. Two-layer architecture (hot cache + knowledge wiki), safety hooks, /close-day end-of-day synthesis. Zero external dependencies."' in text, "expected to find: " + 'description: "Persistent memory system for Claude Code. Two-layer architecture (hot cache + knowledge wiki), safety hooks, /close-day end-of-day synthesis. Zero external dependencies."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-memory-kit/SKILL.md')
    assert "700+ sessions across 7 projects. Adapted from Karpathy/Cole Medin's knowledge base pattern, simplified for daily CLI use." in text, "expected to find: " + "700+ sessions across 7 projects. Adapted from Karpathy/Cole Medin's knowledge base pattern, simplified for daily CLI use."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-memory-kit/SKILL.md')
    assert '- **Persistent memory** — MEMORY.md hot cache + knowledge wiki with [[wikilinks]]' in text, "expected to find: " + '- **Persistent memory** — MEMORY.md hot cache + knowledge wiki with [[wikilinks]]'[:80]

