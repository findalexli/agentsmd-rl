"""Behavioral checks for pilot-docsclaude-scope-navigatoronly-rules-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**If this is an interactive dev session**, use Navigator to plan and Pilot' in text, "expected to find: " + '**If this is an interactive dev session**, use Navigator to plan and Pilot'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'against this very repo to implement tickets. That means this `CLAUDE.md`' in text, "expected to find: " + 'against this very repo to implement tickets. That means this `CLAUDE.md`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Pilot-executor sessions** — spawned by `pilot start` to implement a' in text, "expected to find: " + '1. **Pilot-executor sessions** — spawned by `pilot start` to implement a'[:80]

