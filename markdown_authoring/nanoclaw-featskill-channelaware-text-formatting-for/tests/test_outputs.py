"""Behavioral checks for nanoclaw-featskill-channelaware-text-formatting-for (markdown_authoring task).

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
    text = _read('.claude/skills/channel-formatting/SKILL.md')
    assert "description: Convert Claude's Markdown output to each channel's native text syntax before delivery. Adds zero-dependency formatting for WhatsApp, Telegram, and Slack (marker substitution). Also ships " in text, "expected to find: " + "description: Convert Claude's Markdown output to each channel's native text syntax before delivery. Adds zero-dependency formatting for WhatsApp, Telegram, and Slack (marker substitution). Also ships "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/channel-formatting/SKILL.md')
    assert '| Signal | passthrough for `parseTextStyles`; `parseSignalStyles` in `src/text-styles.ts` produces plain text + native `textStyle` ranges for use by the Signal skill |' in text, "expected to find: " + '| Signal | passthrough for `parseTextStyles`; `parseSignalStyles` in `src/text-styles.ts` produces plain text + native `textStyle` ranges for use by the Signal skill |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/channel-formatting/SKILL.md')
    assert '| WhatsApp | `**bold**` → `*bold*`, `*italic*` → `_italic_`, headings → bold, links flattened |' in text, "expected to find: " + '| WhatsApp | `**bold**` → `*bold*`, `*italic*` → `_italic_`, headings → bold, links flattened |'[:80]

