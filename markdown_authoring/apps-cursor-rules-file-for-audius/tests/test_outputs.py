"""Behavioral checks for apps-cursor-rules-file-for-audius (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/apps")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/audius-style-guide.mdc')
    assert 'description: TypeScript/React coding standards - prefer null coalescing, optional chaining, ternaries for rendering, optional types, and organized string constants' in text, "expected to find: " + 'description: TypeScript/React coding standards - prefer null coalescing, optional chaining, ternaries for rendering, optional types, and organized string constants'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/audius-style-guide.mdc')
    assert 'Organize user-facing strings in a `messages` object at the top of components.' in text, "expected to find: " + 'Organize user-facing strings in a `messages` object at the top of components.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/audius-style-guide.mdc')
    assert "(user && user.profile && user.profile.displayName) || 'Unknown'" in text, "expected to find: " + "(user && user.profile && user.profile.displayName) || 'Unknown'"[:80]

