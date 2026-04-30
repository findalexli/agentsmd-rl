"""Behavioral checks for langchain-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/langchain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "If there's a **cleaner**, **more scalable**, or **simpler** design, highlight it and suggest improvements that would:" in text, "expected to find: " + "If there's a **cleaner**, **more scalable**, or **simpler** design, highlight it and suggest improvements that would:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Always attempt to preserve function signatures, argument positions, and names for exported/public methods.**' in text, "expected to find: " + '**Always attempt to preserve function signatures, argument positions, and names for exported/public methods.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Mark experimental features clearly with docstring warnings (using reStructuredText, like `.. warning::`)' in text, "expected to find: " + '- Mark experimental features clearly with docstring warnings (using reStructuredText, like `.. warning::`)'[:80]

