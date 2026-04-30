"""Behavioral checks for nanoclaw-add-slack-formatting-skill-and (markdown_authoring task).

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
    text = _read('container/skills/slack-formatting/SKILL.md')
    assert 'description: Format messages for Slack using mrkdwn syntax. Use when responding to Slack channels (folder starts with "slack_" or JID contains slack identifiers).' in text, "expected to find: " + 'description: Format messages for Slack using mrkdwn syntax. Use when responding to Slack channels (folder starts with "slack_" or JID contains slack identifiers).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/slack-formatting/SKILL.md')
    assert "When responding to Slack channels, use Slack's mrkdwn syntax instead of standard Markdown." in text, "expected to find: " + "When responding to Slack channels, use Slack's mrkdwn syntax instead of standard Markdown."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/slack-formatting/SKILL.md')
    assert ':white_check_mark: All tests passing | <https://ci.example.com/builds/123|View Build>' in text, "expected to find: " + ':white_check_mark: All tests passing | <https://ci.example.com/builds/123|View Build>'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/global/CLAUDE.md')
    assert "Format messages based on the channel you're responding to. Check your group folder name:" in text, "expected to find: " + "Format messages based on the channel you're responding to. Check your group folder name:"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/global/CLAUDE.md')
    assert 'Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:' in text, "expected to find: " + 'Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/global/CLAUDE.md')
    assert '### WhatsApp/Telegram channels (folder starts with `whatsapp_` or `telegram_`)' in text, "expected to find: " + '### WhatsApp/Telegram channels (folder starts with `whatsapp_` or `telegram_`)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/main/CLAUDE.md')
    assert 'Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:' in text, "expected to find: " + 'Use Slack mrkdwn syntax. Run `/slack-formatting` for the full reference. Key rules:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/main/CLAUDE.md')
    assert 'Format messages based on the channel. Check the group folder name prefix:' in text, "expected to find: " + 'Format messages based on the channel. Check the group folder name prefix:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('groups/main/CLAUDE.md')
    assert 'Standard Markdown: `**bold**`, `*italic*`, `[links](url)`, `# headings`.' in text, "expected to find: " + 'Standard Markdown: `**bold**`, `*italic*`, `[links](url)`, `# headings`.'[:80]

