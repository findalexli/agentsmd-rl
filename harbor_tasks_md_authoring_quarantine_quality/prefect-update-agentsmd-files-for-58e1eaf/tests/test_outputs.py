"""Behavioral checks for prefect-update-agentsmd-files-for-58e1eaf (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '- Place success/completion callbacks (e.g., `onDelete`, `onReset`) in `onSuccess`, **not** `onSettled` — `onSettled` fires on both success and failure, which closes dialogs before the user can see the' in text, "expected to find: " + '- Place success/completion callbacks (e.g., `onDelete`, `onReset`) in `onSuccess`, **not** `onSettled` — `onSettled` fires on both success and failure, which closes dialogs before the user can see the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '- Use `toast.error(message)` to surface mutation errors to the user — never `console.error`' in text, "expected to find: " + '- Use `toast.error(message)` to surface mutation errors to the user — never `console.error`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/components/AGENTS.md')
    assert '## Mutation Error Handling' in text, "expected to find: " + '## Mutation Error Handling'[:80]

