"""Behavioral checks for skills-fixheygenavatar-agentfirst-default-promptbased-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. ' in text, "expected to find: " + '2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert "**When unsure, default to agent.** Do NOT ask the user for their name, appearance, or voice on an ambiguous request — that's the wrong first move. If after reading IDENTITY.md + SOUL.md the intent sti" in text, "expected to find: " + "**When unsure, default to agent.** Do NOT ask the user for their name, appearance, or voice on an ambiguous request — that's the wrong first move. If after reading IDENTITY.md + SOUL.md the intent sti"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '1. **User** (explicit only) — "create **my** avatar", "make **me** an avatar", "I want my face in a video", "a digital twin of **me**", "based on **my** photo". Requires a possessive pronoun referring' in text, "expected to find: " + '1. **User** (explicit only) — "create **my** avatar", "make **me** an avatar", "I want my face in a video", "a digital twin of **me**", "based on **my** photo". Requires a possessive pronoun referring'[:80]

