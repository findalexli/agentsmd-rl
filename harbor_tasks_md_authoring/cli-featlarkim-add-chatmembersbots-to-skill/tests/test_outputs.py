"""Behavioral checks for cli-featlarkim-add-chatmembersbots-to-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-im/SKILL.md')
    assert '- `bots` — 获取群内机器人列表。 Identity: supports `user` and `bot`; the caller must be in the target chat and must belong to the same tenant for internal chats.' in text, "expected to find: " + '- `bots` — 获取群内机器人列表。 Identity: supports `user` and `bot`; the caller must be in the target chat and must belong to the same tenant for internal chats.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-im/SKILL.md')
    assert '| `chat.members.bots` | `im:chat.members:read` |' in text, "expected to find: " + '| `chat.members.bots` | `im:chat.members:read` |'[:80]

