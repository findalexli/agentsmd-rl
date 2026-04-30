"""Behavioral checks for agentrove-newferules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentrove")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Do not use absolute positioning for layout of sibling elements within a container — use flexbox (`flex`, `justify-between`, `gap-*`); reserve `absolute` for overlays, tooltips, dropdowns, and decora' in text, "expected to find: " + '- Do not use absolute positioning for layout of sibling elements within a container — use flexbox (`flex`, `justify-between`, `gap-*`); reserve `absolute` for overlays, tooltips, dropdowns, and decora'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Do not use semantic colors (`error-*`, `warning-*`, `success-*`) for interactive button backgrounds — use monochrome surface tokens; semantic colors are for status badges and text indicators only' in text, "expected to find: " + '- Do not use semantic colors (`error-*`, `warning-*`, `success-*`) for interactive button backgrounds — use monochrome surface tokens; semantic colors are for status badges and text indicators only'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Every `dark:text-*` / `dark:bg-*` class must have a corresponding light-mode class — never rely on browser defaults or inherited color for one mode while explicitly setting the other' in text, "expected to find: " + '- Every `dark:text-*` / `dark:bg-*` class must have a corresponding light-mode class — never rely on browser defaults or inherited color for one mode while explicitly setting the other'[:80]

