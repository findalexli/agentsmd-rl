"""Behavioral checks for cockroach-claudemd-avoid-f-hack-when (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cockroach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Build the tests in package ./pkg/util/log' in text, "expected to find: " + '# Build the tests in package ./pkg/util/log'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert './dev build pkg/util/log:log_test' in text, "expected to find: " + './dev build pkg/util/log:log_test'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert './dev build pkg/util/log' in text, "expected to find: " + './dev build pkg/util/log'[:80]

