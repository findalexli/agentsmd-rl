"""Behavioral checks for rtk-fix-remove-personal-preferences-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rtk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Never assume** which project to work in. Always verify before file operations.' in text, "expected to find: " + '**Never assume** which project to work in. Always verify before file operations.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "pwd  # Verify you're in the rtk project root" in text, "expected to find: " + "pwd  # Verify you're in the rtk project root"[:80]

