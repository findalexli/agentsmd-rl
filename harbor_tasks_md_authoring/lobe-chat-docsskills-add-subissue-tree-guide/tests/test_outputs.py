"""Behavioral checks for lobe-chat-docsskills-add-subissue-tree-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobe-chat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert 'The Linear Sub-issues panel displays children by `sortOrder`, which **defaults to newest-first** (most recently created appears on top). Neither parallel nor serial creation will produce the intended ' in text, "expected to find: " + 'The Linear Sub-issues panel displays children by `sortOrder`, which **defaults to newest-first** (most recently created appears on top). Neither parallel nor serial creation will produce the intended '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert 'MCP tool calls in a single message look parallel but execute sequentially on the server, and you still need blocker IDs from earlier responses. Just issue calls in dependency order; optimizing for par' in text, "expected to find: " + 'MCP tool calls in a single message look parallel but execute sequentially on the server, and you still need blocker IDs from earlier responses. Just issue calls in dependency order; optimizing for par'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert 'Even when the panel shuffles, the reader can mentally reconstruct the dependency graph at a glance. Dotted numbering `[n.m.k]` should mirror the parent-child nesting so the index and the tree agree.' in text, "expected to find: " + 'Even when the panel shuffles, the reader can mentally reconstruct the dependency graph at a glance. Dotted numbering `[n.m.k]` should mirror the parent-child nesting so the index and the tree agree.'[:80]

