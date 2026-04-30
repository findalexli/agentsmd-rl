"""Behavioral checks for angular-docs-add-testing-tips-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/angular")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Zoneless & Async-First:** Assume a zoneless environment where state changes schedule updates asynchronously.' in text, "expected to find: " + '- **Zoneless & Async-First:** Assume a zoneless environment where state changes schedule updates asynchronously.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `await timeout(ms)` (from `packages/private/testing/src/utils.ts`) to wait a specific number of milliseconds.' in text, "expected to find: " + '- `await timeout(ms)` (from `packages/private/testing/src/utils.ts`) to wait a specific number of milliseconds.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `useAutoTick()` (from `packages/private/testing/src/utils.ts`) to fast-forward time via the mock clock.' in text, "expected to find: " + '- Use `useAutoTick()` (from `packages/private/testing/src/utils.ts`) to fast-forward time via the mock clock.'[:80]

