"""Behavioral checks for relay-docs-document-dm-conversation-read (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/relay")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/openclaw/skill/SKILL.md')
    assert '**Dual-auth endpoints:** Some read endpoints require the **workspace key** (`rk_live_...`) rather than the agent token. Specifically, reading DM conversation messages (`GET /v1/dm/conversations/:id/me' in text, "expected to find: " + '**Dual-auth endpoints:** Some read endpoints require the **workspace key** (`rk_live_...`) rather than the agent token. Specifically, reading DM conversation messages (`GET /v1/dm/conversations/:id/me'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/openclaw/skill/SKILL.md')
    assert '> **Note:** Listing conversations (`GET /v1/dm/conversations`) works with just the agent token, but reading message content within a conversation requires the workspace key. See the Token model sectio' in text, "expected to find: " + '> **Note:** Listing conversations (`GET /v1/dm/conversations`) works with just the agent token, but reading message content within a conversation requires the workspace key. See the Token model sectio'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/openclaw/skill/SKILL.md')
    assert '**Reading messages inside a DM conversation** requires dual auth — the workspace key (`rk_live_...`) as `Authorization` and the agent token (`at_live_...`) as `X-Agent-Token`:' in text, "expected to find: " + '**Reading messages inside a DM conversation** requires dual auth — the workspace key (`rk_live_...`) as `Authorization` and the agent token (`at_live_...`) as `X-Agent-Token`:'[:80]

