"""Behavioral checks for tikmatrix-desktop-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tikmatrix-desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'TikMatrix Desktop is a social media automation matrix management software that controls multiple (1-100) Android phones through PC software for real-time screen mirroring, task scheduling, account man' in text, "expected to find: " + 'TikMatrix Desktop is a social media automation matrix management software that controls multiple (1-100) Android phones through PC software for real-time screen mirroring, task scheduling, account man'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Simplicity First**: Avoid over-engineering. Keep code simple, understandable, and practical' in text, "expected to find: " + '1. **Simplicity First**: Avoid over-engineering. Keep code simple, understandable, and practical'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. **Minimal Changes**: When modifying code, minimize changes and avoid affecting other modules' in text, "expected to find: " + '4. **Minimal Changes**: When modifying code, minimize changes and avoid affecting other modules'[:80]

