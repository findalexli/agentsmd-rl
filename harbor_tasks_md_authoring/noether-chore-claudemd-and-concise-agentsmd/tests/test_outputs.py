"""Behavioral checks for noether-chore-claudemd-and-concise-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/noether")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'when appropriate include Examples in Sphinx syntax with the testcode directive.' in text, "expected to find: " + 'when appropriate include Examples in Sphinx syntax with the testcode directive.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Follow Google-style or NumPy-style docstring conventions,' in text, "expected to find: " + 'Follow Google-style or NumPy-style docstring conventions,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Noether is a ML research framework for Engineering AI.' in text, "expected to find: " + 'Noether is a ML research framework for Engineering AI.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See @AGENTS.md for project setup, testing, formatting, and documentation standards.' in text, "expected to find: " + 'See @AGENTS.md for project setup, testing, formatting, and documentation standards.'[:80]

