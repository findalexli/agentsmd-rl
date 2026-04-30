"""Behavioral checks for nanoclaw-add-voice-transcription-skill-using (markdown_authoring task).

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
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert "**UX Note:** When asking the user questions, prefer using the `AskUserQuestion` tool instead of just outputting text. This integrates with Claude's built-in question/answer system for a better experie" in text, "expected to find: " + "**UX Note:** When asking the user questions, prefer using the `AskUserQuestion` tool instead of just outputting text. This integrates with Claude's built-in question/answer system for a better experie"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert "This skill adds automatic voice message transcription using OpenAI's Whisper API. When users send voice notes in WhatsApp, they'll be transcribed and the agent can read and respond to the content." in text, "expected to find: " + "This skill adds automatic voice message transcription using OpenAI's Whisper API. When users send voice notes in WhatsApp, they'll be transcribed and the agent can read and respond to the content."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert "description: Add voice message transcription to NanoClaw using OpenAI's Whisper API. Automatically transcribes WhatsApp voice notes so the agent can read and respond to them." in text, "expected to find: " + "description: Add voice message transcription to NanoClaw using OpenAI's Whisper API. Automatically transcribes WhatsApp voice notes so the agent can read and respond to them."[:80]

