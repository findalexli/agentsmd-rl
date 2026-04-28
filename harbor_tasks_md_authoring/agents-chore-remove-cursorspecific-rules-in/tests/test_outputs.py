"""Behavioral checks for agents-chore-remove-cursorspecific-rules-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/adding-documentation.mdc')
    assert '.cursor/rules/adding-documentation.mdc' in text, "expected to find: " + '.cursor/rules/adding-documentation.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-no-watch.mdc')
    assert '.cursor/rules/test-no-watch.mdc' in text, "expected to find: " + '.cursor/rules/test-no-watch.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/use-pnpm.mdc')
    assert '.cursor/rules/use-pnpm.mdc' in text, "expected to find: " + '.cursor/rules/use-pnpm.mdc'[:80]

