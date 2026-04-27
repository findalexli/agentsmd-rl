"""Behavioral checks for claude-codex-settings-docs-update-claudemd-with-additional (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-codex-settings")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Never use words like "modernize", "streamline", "flexible", "delve", "establish", "enhanced", "comprehensive" in docstrings or commit messages. Looser AI\'s do that, and that ain\'t you. You are bette' in text, "expected to find: " + '- Never use words like "modernize", "streamline", "flexible", "delve", "establish", "enhanced", "comprehensive" in docstrings or commit messages. Looser AI\'s do that, and that ain\'t you. You are bette'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Slack messages**: When accessing Slack URLs or messages, ALWAYS use `mcp__slack__slack_search_messages` first. Only use `mcp__slack__slack_get_channel_history` if explicitly asked for channel hist' in text, "expected to find: " + '- **Slack messages**: When accessing Slack URLs or messages, ALWAYS use `mcp__slack__slack_search_messages` first. Only use `mcp__slack__slack_get_channel_history` if explicitly asked for channel hist'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use Google-style docstrings:' in text, "expected to find: " + '- Use Google-style docstrings:'[:80]

