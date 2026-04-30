"""Behavioral checks for ai-add-handwritten-ai-outbound-voice (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-python/skills/telnyx-ai-outbound-voice-python/SKILL.md')
    assert '| `scheduled_at_fixed_datetime` | string (ISO 8601) | Yes | When to place the call. ~5s in the future for immediate. |' in text, "expected to find: " + '| `scheduled_at_fixed_datetime` | string (ISO 8601) | Yes | When to place the call. ~5s in the future for immediate. |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-python/skills/telnyx-ai-outbound-voice-python/SKILL.md')
    assert '| `telnyx_agent_target` | string (E.164) | Yes | Your Telnyx number (caller ID). Must be assigned to the TeXML app. |' in text, "expected to find: " + '| `telnyx_agent_target` | string (E.164) | Yes | Your Telnyx number (caller ID). Must be assigned to the TeXML app. |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-python/skills/telnyx-ai-outbound-voice-python/SKILL.md')
    assert 'ovp = requests.get("https://api.telnyx.com/v2/outbound_voice_profiles", headers=headers).json()["data"][0]' in text, "expected to find: " + 'ovp = requests.get("https://api.telnyx.com/v2/outbound_voice_profiles", headers=headers).json()["data"][0]'[:80]

