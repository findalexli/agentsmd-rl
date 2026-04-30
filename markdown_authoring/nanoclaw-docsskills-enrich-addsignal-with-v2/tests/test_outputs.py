"""Behavioral checks for nanoclaw-docsskills-enrich-addsignal-with-v2 (markdown_authoring task).

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
    text = _read('.claude/skills/add-signal/SKILL.md')
    assert 'Modern Signal groups use GroupV2. The adapter must extract the group ID from `envelope?.dataMessage?.groupV2?.id` — not `groupInfo?.groupId`, which is GroupV1/legacy. If group messages are routing as ' in text, "expected to find: " + 'Modern Signal groups use GroupV2. The adapter must extract the group ID from `envelope?.dataMessage?.groupV2?.id` — not `groupInfo?.groupId`, which is GroupV1/legacy. If group messages are routing as '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-signal/SKILL.md')
    assert 'The Signal user hasn\'t been granted membership. See "Grant user access" above. This affects every new Signal user, including the owner\'s Signal identity — which is a separate user record from their id' in text, "expected to find: " + 'The Signal user hasn\'t been granted membership. See "Grant user access" above. This affects every new Signal user, including the owner\'s Signal identity — which is a separate user record from their id'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-signal/SKILL.md')
    assert 'Adds Signal messaging support via a native adapter that speaks JSON-RPC to a [signal-cli](https://github.com/AsamK/signal-cli) TCP daemon. No Chat SDK bridge — only Node.js builtins (`node:net`, `node' in text, "expected to find: " + 'Adds Signal messaging support via a native adapter that speaks JSON-RPC to a [signal-cli](https://github.com/AsamK/signal-cli) TCP daemon. No Chat SDK bridge — only Node.js builtins (`node:net`, `node'[:80]

