"""Behavioral checks for prefect-update-agentsmd-files-for-d3fbc09 (markdown_authoring task).

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
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '**Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict' in text, "expected to find: " + '**Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'await expect(page.getByRole("table").getByText(itemName)).not.toBeVisible();' in text, "expected to find: " + 'await expect(page.getByRole("table").getByText(itemName)).not.toBeVisible();'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '// ✅ Good - wait for dialog to close, then scope assertion to the table' in text, "expected to find: " + '// ✅ Good - wait for dialog to close, then scope assertion to the table'[:80]

