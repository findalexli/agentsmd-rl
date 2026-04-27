"""Behavioral checks for antigravity-awesome-skills-feat-add-agentmemory-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-memory/SKILL.md')
    assert 'This skill provides a persistent, searchable memory bank that automatically syncs with project documentation. It runs as an MCP server to allow reading/writing/searching of long-term memories.' in text, "expected to find: " + 'This skill provides a persistent, searchable memory bank that automatically syncs with project documentation. It runs as an MCP server to allow reading/writing/searching of long-term memories.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-memory/SKILL.md')
    assert 'description: A hybrid memory system that provides persistent, searchable knowledge management for AI agents (Architecture, Patterns, Decisions).' in text, "expected to find: " + 'description: A hybrid memory system that provides persistent, searchable knowledge management for AI agents (Architecture, Patterns, Decisions).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-memory/SKILL.md')
    assert '- **Usage**: "Save this architecture decision" -> `memory_write({ key: "auth-v1", type: "decision", content: "..." })`' in text, "expected to find: " + '- **Usage**: "Save this architecture decision" -> `memory_write({ key: "auth-v1", type: "decision", content: "..." })`'[:80]

