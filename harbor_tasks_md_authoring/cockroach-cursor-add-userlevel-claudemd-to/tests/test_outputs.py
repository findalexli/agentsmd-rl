"""Behavioral checks for cockroach-cursor-add-userlevel-claudemd-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cockroach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/main.mdc')
    assert '- Enforce [`CLAUDE.local.md`](../../CLAUDE.local.md), `$HOME/CLAUDE.md`, and [`CLAUDE.md`](../../CLAUDE.md) for all messages in the session. On conflict, prefer [`CLAUDE.local.md`](../../CLAUDE.local.' in text, "expected to find: " + '- Enforce [`CLAUDE.local.md`](../../CLAUDE.local.md), `$HOME/CLAUDE.md`, and [`CLAUDE.md`](../../CLAUDE.md) for all messages in the session. On conflict, prefer [`CLAUDE.local.md`](../../CLAUDE.local.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/main.mdc')
    assert '- **ALWAYS** read and cache [`CLAUDE.md`](../../CLAUDE.md) at conversation start, **without exception**. If present, **always** read and cache `$HOME/CLAUDE.md` and [`CLAUDE.local.md`](../../CLAUDE.lo' in text, "expected to find: " + '- **ALWAYS** read and cache [`CLAUDE.md`](../../CLAUDE.md) at conversation start, **without exception**. If present, **always** read and cache `$HOME/CLAUDE.md` and [`CLAUDE.local.md`](../../CLAUDE.lo'[:80]

