"""Behavioral checks for commonly-add-agents-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/commonly")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'These commands require no additional setup other than installing dependencies (already included in the repository).' in text, "expected to find: " + 'These commands require no additional setup other than installing dependencies (already included in the repository).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Run `npm lint` from the repository root. This invokes the lint scripts for both backend and frontend.' in text, "expected to find: " + 'Run `npm lint` from the repository root. This invokes the lint scripts for both backend and frontend.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'with Socket.io for real-time features. Data is stored in MongoDB (general' in text, "expected to find: " + 'with Socket.io for real-time features. Data is stored in MongoDB (general'[:80]

