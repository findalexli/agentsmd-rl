"""Behavioral checks for zen-desktop-agentsmd-add-agent-instructions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zen-desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the source for Zen - a system-wide proxy-based ad-blocker and privacy guard. Built using Wails as the application framework, Go for core logic, and TS/React for the UI.' in text, "expected to find: " + 'This is the source for Zen - a system-wide proxy-based ad-blocker and privacy guard. Built using Wails as the application framework, Go for core logic, and TS/React for the UI.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prefer `task` commands over manual shell commands' in text, "expected to find: " + '- Prefer `task` commands over manual shell commands'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Format check (frontend): `task frontend:fmt`' in text, "expected to find: " + '- Format check (frontend): `task frontend:fmt`'[:80]

