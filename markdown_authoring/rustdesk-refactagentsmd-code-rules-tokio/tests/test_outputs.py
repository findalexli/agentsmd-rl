"""Behavioral checks for rustdesk-refactagentsmd-code-rules-tokio (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rustdesk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* lock acquisition where failure means poisoning, not normal control flow.' in text, "expected to find: " + '* lock acquisition where failure means poisoning, not normal control flow.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Use `spawn_blocking` or dedicated threads for blocking work.' in text, "expected to find: " + '* Use `spawn_blocking` or dedicated threads for blocking work.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Never call `Runtime::block_on()` inside Tokio / async code.' in text, "expected to find: " + '* Never call `Runtime::block_on()` inside Tokio / async code.'[:80]

