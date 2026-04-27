"""Behavioral checks for memsearch-expand-memoryrecall-skill-description-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/memsearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/claude-code/skills/memory-recall/SKILL.md')
    assert 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver' in text, "expected to find: " + 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/codex/skills/memory-recall/SKILL.md')
    assert 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver' in text, "expected to find: " + 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/openclaw/skills/memory-recall/SKILL.md')
    assert 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver' in text, "expected to find: " + 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/opencode/skills/memory-recall/SKILL.md')
    assert 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver' in text, "expected to find: " + 'description: "Search and recall relevant memories from past sessions via memsearch. Use when the user\'s question could benefit from historical context, past decisions, debugging notes, previous conver'[:80]

