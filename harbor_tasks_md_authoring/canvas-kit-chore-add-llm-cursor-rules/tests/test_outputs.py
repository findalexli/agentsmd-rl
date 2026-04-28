"""Behavioral checks for canvas-kit-chore-add-llm-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/canvas-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('modules/docs/llm/canvas-kit.mdc')
    assert 'The `cs` prop accepts styles created by `createStyles`, `createStencil`, or a class name. Canvas Kit' in text, "expected to find: " + 'The `cs` prop accepts styles created by `createStyles`, `createStencil`, or a class name. Canvas Kit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('modules/docs/llm/canvas-kit.mdc')
    assert 'description: Best practices for Workday Canvas Kit - tokens, styling, components, and accessibility' in text, "expected to find: " + 'description: Best practices for Workday Canvas Kit - tokens, styling, components, and accessibility'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('modules/docs/llm/canvas-kit.mdc')
    assert '- Check whether tabbing is sufficient or if additional keyboard navigation is required (e.g., arrow' in text, "expected to find: " + '- Check whether tabbing is sufficient or if additional keyboard navigation is required (e.g., arrow'[:80]

