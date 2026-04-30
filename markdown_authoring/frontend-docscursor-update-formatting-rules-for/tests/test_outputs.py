"""Behavioral checks for frontend-docscursor-update-formatting-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/frontend")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/formatting-component-files.mdc')
    assert '- When calling `task.perform()` in lifecycle hooks like `handleDidInsert`, use `await` so that tests will properly wait for the async operation to complete' in text, "expected to find: " + '- When calling `task.perform()` in lifecycle hooks like `handleDidInsert`, use `await` so that tests will properly wait for the async operation to complete'[:80]

