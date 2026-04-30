"""Behavioral checks for nim-libp2p-chorecopilot-add-more-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nim-libp2p")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do not use `asyncSpawn` unless the future reference is explicitly tracked. Running a future with `asyncSpawn` without tracking its reference risks the future being freed/deallocated when it becomes ' in text, "expected to find: " + '- Do not use `asyncSpawn` unless the future reference is explicitly tracked. Running a future with `asyncSpawn` without tracking its reference risks the future being freed/deallocated when it becomes '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Usage of `AsyncLock` must always be documented. Provide a clear explanation of why the lock is required in that context. This ensures that locking decisions are transparent, justified, and maintaina' in text, "expected to find: " + '- Usage of `AsyncLock` must always be documented. Provide a clear explanation of why the lock is required in that context. This ensures that locking decisions are transparent, justified, and maintaina'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `cancel()` procedure of `Future` type is deprecated, code should either call `cancelSoon()` for non-blocking call or `cancelAndWait()` for blocking call until the future is canceled/has been cancele' in text, "expected to find: " + '- `cancel()` procedure of `Future` type is deprecated, code should either call `cancelSoon()` for non-blocking call or `cancelAndWait()` for blocking call until the future is canceled/has been cancele'[:80]

