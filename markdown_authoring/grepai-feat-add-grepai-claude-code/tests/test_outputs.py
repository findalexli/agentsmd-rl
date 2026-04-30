"""Behavioral checks for grepai-feat-add-grepai-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/grepai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/grepai/SKILL.md')
    assert 'description: "Replaces ALL built-in search tools. You MUST invoke this skill BEFORE using WebSearch, Grep, or Glob. NEVER use the built-in Grep tool - use `grepai` instead."' in text, "expected to find: " + 'description: "Replaces ALL built-in search tools. You MUST invoke this skill BEFORE using WebSearch, Grep, or Glob. NEVER use the built-in Grep tool - use `grepai` instead."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/grepai/SKILL.md')
    assert 'If grepai fails (not running, index unavailable, or errors), fall back to standard Grep/Glob tools. Common issues:' in text, "expected to find: " + 'If grepai fails (not running, index unavailable, or errors), fall back to standard Grep/Glob tools. Common issues:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/grepai/SKILL.md')
    assert '- Invoke this skill, then use `grepai search "authentication flow"` for semantic search' in text, "expected to find: " + '- Invoke this skill, then use `grepai search "authentication flow"` for semantic search'[:80]

