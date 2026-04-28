"""Behavioral checks for equicord-add-agentsmd-guide-for-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/equicord")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**@webpack/common:** Stores (`UserStore`, `GuildStore`, `ChannelStore`, 30+ more), Actions (`RestAPI`, `FluxDispatcher`, `MessageActions`, `NavigationRouter`), Utils (`Constants.Endpoints`, `Snowflake' in text, "expected to find: " + '**@webpack/common:** Stores (`UserStore`, `GuildStore`, `ChannelStore`, 30+ more), Actions (`RestAPI`, `FluxDispatcher`, `MessageActions`, `NavigationRouter`), Utils (`Constants.Endpoints`, `Snowflake'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**@utils/discord:** `getCurrentChannel`, `getCurrentGuild`, `getIntlMessage`, `openPrivateChannel`, `insertTextIntoChatInputBox`, `sendMessage`, `copyWithToast`, `openUserProfile`, `fetchUserProfile`,' in text, "expected to find: " + '**@utils/discord:** `getCurrentChannel`, `getCurrentGuild`, `getIntlMessage`, `openPrivateChannel`, `insertTextIntoChatInputBox`, `sendMessage`, `copyWithToast`, `openUserProfile`, `fetchUserProfile`,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.** When uncertain about APIs, patterns, or existing implementations, read the relevant source files rather than relying on a' in text, "expected to find: " + '**IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.** When uncertain about APIs, patterns, or existing implementations, read the relevant source files rather than relying on a'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

