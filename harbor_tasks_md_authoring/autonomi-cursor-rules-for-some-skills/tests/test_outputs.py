"""Behavioral checks for autonomi-cursor-rules-for-some-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autonomi")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'Please do not use unwraps or panics. Please ensure all methods are fully tested and annotated.' in text, "expected to find: " + 'Please do not use unwraps or panics. Please ensure all methods are fully tested and annotated.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'This rule set enables automatic detection of task patterns and applies appropriate workflows.' in text, "expected to find: " + 'This rule set enables automatic detection of task patterns and applies appropriate workflows.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert "When the user's prompt contains any of these patterns, apply the deep-researcher workflow:" in text, "expected to find: " + "When the user's prompt contains any of these patterns, apply the deep-researcher workflow:"[:80]

