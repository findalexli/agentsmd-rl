"""Behavioral checks for torchjd-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/torchjd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When you create or modify a code example in a public docstring, always update the corresponding' in text, "expected to find: " + '- When you create or modify a code example in a public docstring, always update the corresponding'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'doc test in the appropriate file of `tests/doc`. This also applies to any change in an example of' in text, "expected to find: " + 'doc test in the appropriate file of `tests/doc`. This also applies to any change in an example of'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'a `.rst` file, that must be updated in the corresponding test in `tests/doc/test_rst.py`.' in text, "expected to find: " + 'a `.rst` file, that must be updated in the corresponding test in `tests/doc/test_rst.py`.'[:80]

