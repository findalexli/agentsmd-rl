"""Behavioral checks for nanoclaw-replace-ask-the-user-with (markdown_authoring task).

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
    text = _read('.claude/skills/add-discord/SKILL.md')
    assert '- **Replace WhatsApp** - Discord will be the only channel (sets DISCORD_ONLY=true)' in text, "expected to find: " + '- **Replace WhatsApp** - Discord will be the only channel (sets DISCORD_ONLY=true)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-discord/SKILL.md')
    assert 'AskUserQuestion: Do you have a Discord bot token, or do you need to create one?' in text, "expected to find: " + 'AskUserQuestion: Do you have a Discord bot token, or do you need to create one?'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-discord/SKILL.md')
    assert "If they have one, collect it now. If not, we'll create one in Phase 3." in text, "expected to find: " + "If they have one, collect it now. If not, we'll create one in Phase 3."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert '- **Email Address Pattern** - Emails to a specific address pattern (e.g., andy+task@gmail.com) via plus-addressing' in text, "expected to find: " + '- **Email Address Pattern** - Emails to a specific address pattern (e.g., andy+task@gmail.com) via plus-addressing'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert '- **Channel Mode** - Emails can trigger the agent, schedule tasks, and receive email replies (requires polling)' in text, "expected to find: " + '- **Channel Mode** - Emails can trigger the agent, schedule tasks, and receive email replies (requires polling)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert '- **Specific Label** - Create a Gmail label (e.g., "NanoClaw"), emails with this label trigger the agent' in text, "expected to find: " + '- **Specific Label** - Create a Gmail label (e.g., "NanoClaw"), emails with this label trigger the agent'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-parallel/SKILL.md')
    assert "AskUserQuestion: I can do deep research on [topic] using Parallel's Task API. This will take 2-5 minutes and provide comprehensive analysis with citations. Should I proceed?" in text, "expected to find: " + "AskUserQuestion: I can do deep research on [topic] using Parallel's Task API. This will take 2-5 minutes and provide comprehensive analysis with citations. Should I proceed?"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-parallel/SKILL.md')
    assert 'Use `AskUserQuestion: Do you have a Parallel AI API key, or should I help you get one?`' in text, "expected to find: " + 'Use `AskUserQuestion: Do you have a Parallel AI API key, or should I help you get one?`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-parallel/SKILL.md')
    assert '**Permission:** ALWAYS use `AskUserQuestion` before using this tool' in text, "expected to find: " + '**Permission:** ALWAYS use `AskUserQuestion` before using this tool'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-telegram/SKILL.md')
    assert 'AskUserQuestion: Would you like to add Agent Swarm support? Without it, Agent Teams still work — they just operate behind the scenes. With Swarm support, each subagent appears as a different bot in th' in text, "expected to find: " + 'AskUserQuestion: Would you like to add Agent Swarm support? Without it, Agent Teams still work — they just operate behind the scenes. With Swarm support, each subagent appears as a different bot in th'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-telegram/SKILL.md')
    assert '- **Replace WhatsApp** - Telegram will be the only channel (sets TELEGRAM_ONLY=true)' in text, "expected to find: " + '- **Replace WhatsApp** - Telegram will be the only channel (sets TELEGRAM_ONLY=true)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-telegram/SKILL.md')
    assert 'AskUserQuestion: Do you have a Telegram bot token, or do you need to create one?' in text, "expected to find: " + 'AskUserQuestion: Do you have a Telegram bot token, or do you need to create one?'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert 'If yes, collect it now. If no, direct them to create one at https://platform.openai.com/api-keys.' in text, "expected to find: " + 'If yes, collect it now. If no, direct them to create one at https://platform.openai.com/api-keys.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert 'AskUserQuestion: Do you have an OpenAI API key for Whisper transcription?' in text, "expected to find: " + 'AskUserQuestion: Do you have an OpenAI API key for Whisper transcription?'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert 'Use `AskUserQuestion` to collect information:' in text, "expected to find: " + 'Use `AskUserQuestion` to collect information:'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '- PLATFORM=macos + APPLE_CONTAINER=installed → Use `AskUserQuestion: Docker (default, cross-platform) or Apple Container (native macOS)?` If Apple Container, run `/convert-to-apple-container` now, the' in text, "expected to find: " + '- PLATFORM=macos + APPLE_CONTAINER=installed → Use `AskUserQuestion: Docker (default, cross-platform) or Apple Container (native macOS)?` If Apple Container, run `/convert-to-apple-container` now, the'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '- If NODE_OK=false → Node.js is missing or too old. Use `AskUserQuestion: Would you like me to install Node.js 22?` If confirmed:' in text, "expected to find: " + '- If NODE_OK=false → Node.js is missing or too old. Use `AskUserQuestion: Would you like me to install Node.js 22?` If confirmed:'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup/SKILL.md')
    assert '- DOCKER=not_found → Use `AskUserQuestion: Docker is required for running agents. Would you like me to install it?` If confirmed:' in text, "expected to find: " + '- DOCKER=not_found → Use `AskUserQuestion: Docker is required for running agents. Would you like me to install it?` If confirmed:'[:80]

