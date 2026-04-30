"""Behavioral checks for skills-fixheygenavatar-before-you-start-block (markdown_authoring task).

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
    assert '**⚠️ Do NOT fetch HeyGen avatars yet.** That\'s a Phase 0 sub-step (only after target detection). Fetching before Phase 0 causes the agent to frame the conversation around "your existing avatars" when ' in text, "expected to find: " + '**⚠️ Do NOT fetch HeyGen avatars yet.** That\'s a Phase 0 sub-step (only after target detection). Fetching before Phase 0 causes the agent to frame the conversation around "your existing avatars" when '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert 'If the list is non-empty, present the options and ask which to use or whether to create new. If empty, proceed to Phase 1. Skip this check entirely for agent and named-character targets — those live i' in text, "expected to find: " + 'If the list is non-empty, present the options and ask which to use or whether to create new. If empty, proceed to Phase 1. Skip this check entirely for agent and named-character targets — those live i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**Optional existing-avatar check** (only useful on the user path when the user might already have avatars in their HeyGen account). If Phase 0 target = **user** AND no `AVATAR-<USER>.md` exists, list ' in text, "expected to find: " + '**Optional existing-avatar check** (only useful on the user path when the user might already have avatars in their HeyGen account). If Phase 0 target = **user** AND no `AVATAR-<USER>.md` exists, list '[:80]

