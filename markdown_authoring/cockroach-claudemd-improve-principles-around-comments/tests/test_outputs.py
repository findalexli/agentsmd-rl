"""Behavioral checks for cockroach-claudemd-improve-principles-around-comments (markdown_authoring task).

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
    assert 'Explain concepts/abstractions, show how pieces fit together, connect to use cases. These must be understandable without reading any code - define terms clearly and use examples to illustrate abstract ' in text, "expected to find: " + 'Explain concepts/abstractions, show how pieces fit together, connect to use cases. These must be understandable without reading any code - define terms clearly and use examples to illustrate abstract '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Document the purpose, lifecycle, and usage of each field. This is where data structure details belong - function comments should not repeat this information.' in text, "expected to find: " + 'Document the purpose, lifecycle, and usage of each field. This is where data structure details belong - function comments should not repeat this information.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Algorithmic comments that separate different processing phases and explain non-obvious logic. These belong inside functions, not at function declarations.' in text, "expected to find: " + 'Algorithmic comments that separate different processing phases and explain non-obvious logic. These belong inside functions, not at function declarations.'[:80]

