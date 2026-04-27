"""Behavioral checks for compound-engineering-plugin-fixcedebug-stop-hanging-handoffs (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert "**If Phase 3 ran**, immediately after the summary prompt the user for the next action via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_u" in text, "expected to find: " + "**If Phase 3 ran**, immediately after the summary prompt the user for the next action via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_u"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert 'Read the full conversation — the original description AND every comment, with particular attention to the latest ones. Comments frequently contain updated reproduction steps, narrowed scope, prior fai' in text, "expected to find: " + 'Read the full conversation — the original description AND every comment, with particular attention to the latest ones. Comments frequently contain updated reproduction steps, narrowed scope, prior fai'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert "Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first" in text, "expected to find: " + "Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first"[:80]

