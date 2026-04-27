"""Behavioral checks for aionui-choreskills-improve-osspr-quality-checks (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/oss-pr/SKILL.md')
    assert '1. bun run format (ALWAYS) && bun run lint && bunx tsc --noEmit (skip lint/tsc if no .ts/.tsx)' in text, "expected to find: " + '1. bun run format (ALWAYS) && bun run lint && bunx tsc --noEmit (skip lint/tsc if no .ts/.tsx)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/oss-pr/SKILL.md')
    assert '| Command             | Scope                     | Skip when                   |' in text, "expected to find: " + '| Command             | Scope                     | Skip when                   |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/oss-pr/SKILL.md')
    assert '| `bun run format`    | `.ts/.tsx/.css/.json/.md` | **Never** — always run      |' in text, "expected to find: " + '| `bun run format`    | `.ts/.tsx/.css/.json/.md` | **Never** — always run      |'[:80]

