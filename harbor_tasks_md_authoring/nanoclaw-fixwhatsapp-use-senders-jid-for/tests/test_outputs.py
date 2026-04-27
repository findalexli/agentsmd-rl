"""Behavioral checks for nanoclaw-fixwhatsapp-use-senders-jid-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-whatsapp/SKILL.md')
    assert "AskUserQuestion: What is your personal phone number? (The number you'll use to message the bot — include country code without +, e.g. 1234567890)" in text, "expected to find: " + "AskUserQuestion: What is your personal phone number? (The number you'll use to message the bot — include country code without +, e.g. 1234567890)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-whatsapp/SKILL.md')
    assert "**DM with bot:** The JID is the **user's** phone number — the number they will message *from* (not the bot's own number). Ask:" in text, "expected to find: " + "**DM with bot:** The JID is the **user's** phone number — the number they will message *from* (not the bot's own number). Ask:"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-whatsapp/SKILL.md')
    assert "--no-trigger-required  # For self-chat and DM with bot (1:1 conversations don't need a trigger prefix)" in text, "expected to find: " + "--no-trigger-required  # For self-chat and DM with bot (1:1 conversations don't need a trigger prefix)"[:80]

