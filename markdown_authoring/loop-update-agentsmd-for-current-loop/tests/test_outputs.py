"""Behavioral checks for loop-update-agentsmd-for-current-loop (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/loop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Running `loop` with no args starts the paired interactive tmux workspace (`--tmux`); `loop dashboard` opens the live panel for active sessions, loop-owned paired runs, and tmux sessions. Keep panel-' in text, "expected to find: " + '- Running `loop` with no args starts the paired interactive tmux workspace (`--tmux`); `loop dashboard` opens the live panel for active sessions, loop-owned paired runs, and tmux sessions. Keep panel-'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When options are provided without a prompt, `loop` reuses `PLAN.md` if it already exists; keep that fallback aligned with the plain-text prompt planning flow.' in text, "expected to find: " + '- When options are provided without a prompt, `loop` reuses `PLAN.md` if it already exists; keep that fallback aligned with the plain-text prompt planning flow.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Install global binary/aliases: `bun run install:global`' in text, "expected to find: " + '- Install global binary/aliases: `bun run install:global`'[:80]

