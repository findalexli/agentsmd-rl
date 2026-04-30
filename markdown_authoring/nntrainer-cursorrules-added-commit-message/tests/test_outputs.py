"""Behavioral checks for nntrainer-cursorrules-added-commit-message (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nntrainer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- If the commit is a bugfix; it should describe the bug and how it is resolved.' in text, "expected to find: " + '- If the commit is a bugfix; it should describe the bug and how it is resolved.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- If the commit is a new feature; it should describe the feature itself.' in text, "expected to find: " + '- If the commit is a new feature; it should describe the feature itself.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- The commit message should summarize the commit itself.' in text, "expected to find: " + '- The commit message should summarize the commit itself.'[:80]

