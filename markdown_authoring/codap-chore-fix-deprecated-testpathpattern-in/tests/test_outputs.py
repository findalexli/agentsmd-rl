"""Behavioral checks for codap-chore-fix-deprecated-testpathpattern-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/codap")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Run tests matching a pattern (pass the pattern directly, NOT via --testPathPattern which is deprecated)' in text, "expected to find: " + '# Run tests matching a pattern (pass the pattern directly, NOT via --testPathPattern which is deprecated)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'npm test -- data-set' in text, "expected to find: " + 'npm test -- data-set'[:80]

