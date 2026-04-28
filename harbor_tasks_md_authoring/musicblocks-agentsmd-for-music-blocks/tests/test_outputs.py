"""Behavioral checks for musicblocks-agentsmd-for-music-blocks (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/musicblocks")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Ask the user for a browser check when the change affects UI, widgets, drag/drop, rendering, audio, persistence, startup behavior, or another interaction that tests do not fully cover.' in text, "expected to find: " + 'Ask the user for a browser check when the change affects UI, widgets, drag/drop, rendering, audio, persistence, startup behavior, or another interaction that tests do not fully cover.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Verify the intended fix and the nearest related behavior so the change is not correct only for one narrow case.' in text, "expected to find: " + '- Verify the intended fix and the nearest related behavior so the change is not correct only for one narrow case.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- wrong block behavior -> relevant file in `js/blocks/` and matching file in `js/turtleactions/`' in text, "expected to find: " + '- wrong block behavior -> relevant file in `js/blocks/` and matching file in `js/turtleactions/`'[:80]

