"""Behavioral checks for agno-chore-add-comprehensive-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agno")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'You are an expert in Python, Agno framework, and AI agent development.' in text, "expected to find: " + 'You are an expert in Python, Agno framework, and AI agent development.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- NEVER create agents in loops - reuse them for performance' in text, "expected to find: " + '- NEVER create agents in loops - reuse them for performance'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '# WRONG - Recreates agent every time (significant overhead)' in text, "expected to find: " + '# WRONG - Recreates agent every time (significant overhead)'[:80]

