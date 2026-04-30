"""Behavioral checks for splitrail-add-a-sample-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/splitrail")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-new-supported-agent/SKILL.md')
    assert 'description: Add support for a new AI coding agent/CLI tool. Use when implementing tracking for a new tool like a new Cline fork, coding CLI, or VS Code extension.' in text, "expected to find: " + 'description: Add support for a new AI coding agent/CLI tool. Use when implementing tracking for a new tool like a new Cline fork, coding CLI, or VS Code extension.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-new-supported-agent/SKILL.md')
    assert 'Splitrail tracks token usage from AI coding agents. Each agent has its own "analyzer" that discovers and parses its data files.' in text, "expected to find: " + 'Splitrail tracks token usage from AI coding agents. Each agent has its own "analyzer" that discovers and parses its data files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-new-supported-agent/SKILL.md')
    assert 'async fn parse_conversations(&self, sources: Vec<DataSource>) -> Result<Vec<ConversationMessage>> {' in text, "expected to find: " + 'async fn parse_conversations(&self, sources: Vec<DataSource>) -> Result<Vec<ConversationMessage>> {'[:80]

