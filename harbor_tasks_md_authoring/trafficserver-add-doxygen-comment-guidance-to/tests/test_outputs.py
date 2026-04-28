"""Behavioral checks for trafficserver-add-doxygen-comment-guidance-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/trafficserver")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- In the description of classes, functions, and member variables, convey the' in text, "expected to find: " + '- In the description of classes, functions, and member variables, convey the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `@ref`, `@see`, or `@sa` to cross-reference related types or functions' in text, "expected to find: " + '- Use `@ref`, `@see`, or `@sa` to cross-reference related types or functions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `@brief` is assumed for the first sentence, so give a brief summary right' in text, "expected to find: " + '- `@brief` is assumed for the first sentence, so give a brief summary right'[:80]

