"""Behavioral checks for zulip-ai-claude-add-lessons-learned (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zulip")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- For zoomed clips, calculate the clip region from non-fixed elements;' in text, "expected to find: " + '- For zoomed clips, calculate the clip region from non-fixed elements;'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- Use `em` units instead of `px` for computed CSS values that need to' in text, "expected to find: " + '- Use `em` units instead of `px` for computed CSS values that need to'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'scale with font size. Pixel approximations break at different zoom' in text, "expected to find: " + 'scale with font size. Pixel approximations break at different zoom'[:80]

