"""Behavioral checks for claude-code-templates-featskills-add-claudecodesessions-prod (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/productivity/claude-code-sessions/SKILL.md')
    assert 'Claude Code records every session as a JSONL file — messages, tool calls, token counts, diffs, tasks. This plugin reads those files and provides two interfaces. Most operations are read-only; delete a' in text, "expected to find: " + 'Claude Code records every session as a JSONL file — messages, tool calls, token counts, diffs, tasks. This plugin reads those files and provides two interfaces. Most operations are read-only; delete a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/productivity/claude-code-sessions/SKILL.md')
    assert 'description: Search, analyze, and manage Claude Code session history. Use when the user wants to find past sessions, check token usage, review tool breakdowns, resume previous work, or manage tasks ac' in text, "expected to find: " + 'description: Search, analyze, and manage Claude Code session history. Use when the user wants to find past sessions, check token usage, review tool breakdowns, resume previous work, or manage tasks ac'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/productivity/claude-code-sessions/SKILL.md')
    assert '**Web dashboard** at `localhost:3000` with four views: Dashboard (summary stats), Sessions (sortable table with bulk operations), Search (full-text with context snippets), Tasks (grouped by status wit' in text, "expected to find: " + '**Web dashboard** at `localhost:3000` with four views: Dashboard (summary stats), Sessions (sortable table with bulk operations), Search (full-text with context snippets), Tasks (grouped by status wit'[:80]

