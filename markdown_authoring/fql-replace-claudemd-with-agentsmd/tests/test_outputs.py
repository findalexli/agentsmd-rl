"""Behavioral checks for fql-replace-claudemd-with-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides guidance for AI coding agents working with code in this repository.' in text, "expected to find: " + 'This file provides guidance for AI coding agents working with code in this repository.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- FDB container automatically managed for tests' in text, "expected to find: " + '- FDB container automatically managed for tests'[:80]

