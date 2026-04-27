"""Behavioral checks for buildwithclaude-add-slackmessageformatter-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/slack-message-formatter/SKILL.md')
    assert 'The preview shows a pixel-perfect Slack UI rendering. The user pastes directly into Slack with Cmd+V / Ctrl+V and the formatting is preserved.' in text, "expected to find: " + 'The preview shows a pixel-perfect Slack UI rendering. The user pastes directly into Slack with Cmd+V / Ctrl+V and the formatting is preserved.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/slack-message-formatter/SKILL.md')
    assert "2. **Converts to Rich HTML** — Transforms Markdown into rich HTML that preserves formatting when pasted into Slack's compose box" in text, "expected to find: " + "2. **Converts to Rich HTML** — Transforms Markdown into rich HTML that preserves formatting when pasted into Slack's compose box"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/slack-message-formatter/SKILL.md')
    assert 'Format messages for Slack with pixel-perfect accuracy. Converts Markdown to Slack-compatible output with two delivery paths:' in text, "expected to find: " + 'Format messages for Slack with pixel-perfect accuracy. Converts Markdown to Slack-compatible output with two delivery paths:'[:80]

