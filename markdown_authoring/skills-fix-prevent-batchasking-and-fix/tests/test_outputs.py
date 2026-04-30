"""Behavioral checks for skills-fix-prevent-batchasking-and-fix (markdown_authoring task).

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
    text = _read('SKILL.md')
    assert '5. **Don\'t batch-ask across skills.** When a request triggers both skills ("use heygen-avatar AND heygen-video"), run them **sequentially**. Complete heygen-avatar first (identity → avatar ready), the' in text, "expected to find: " + '5. **Don\'t batch-ask across skills.** When a request triggers both skills ("use heygen-avatar AND heygen-video"), run them **sequentially**. Complete heygen-avatar first (identity → avatar ready), the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '6. **Read workspace files before asking.** `SOUL.md`, `IDENTITY.md`, and `AVATAR-<NAME>.md` at the workspace root contain identity and existing avatar state. Check them first. Only ask the user for wh' in text, "expected to find: " + '6. **Read workspace files before asking.** `SOUL.md`, `IDENTITY.md`, and `AVATAR-<NAME>.md` at the workspace root contain identity and existing avatar state. Check them first. Only ask the user for wh'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. ' in text, "expected to find: " + '2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**When creating for the agent itself** ("create your avatar", "bring yourself to life"), do NOT ask the user for a photo or appearance details first. Read `SOUL.md` and `IDENTITY.md` from the workspac' in text, "expected to find: " + '**When creating for the agent itself** ("create your avatar", "bring yourself to life"), do NOT ask the user for a photo or appearance details first. Read `SOUL.md` and `IDENTITY.md` from the workspac'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-avatar/SKILL.md')
    assert '**Do NOT batch-ask questions.** Do not fire "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two thin' in text, "expected to find: " + '**Do NOT batch-ask questions.** Do not fire "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two thin'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert '**DO NOT batch-ask all of these at once.** Ask one or two items at a time. Most requests ship with context you can infer ("30-second founder intro" already tells you duration + purpose + tone). Only a' in text, "expected to find: " + '**DO NOT batch-ask all of these at once.** Ask one or two items at a time. Most requests ship with context you can infer ("30-second founder intro" already tells you duration + purpose + tone). Only a'[:80]

