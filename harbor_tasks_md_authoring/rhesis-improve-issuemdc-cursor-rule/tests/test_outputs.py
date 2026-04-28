"""Behavioral checks for rhesis-improve-issuemdc-cursor-rule (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rhesis")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/issue.mdc')
    assert '1. The issue could be either a "Bug", "Feature" or a "Task", set up a correct template for the issue.' in text, "expected to find: " + '1. The issue could be either a "Bug", "Feature" or a "Task", set up a correct template for the issue.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/issue.mdc')
    assert '3. List the existing labels using `gh label list` and select the appropriate label for the issue.' in text, "expected to find: " + '3. List the existing labels using `gh label list` and select the appropriate label for the issue.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/issue.mdc')
    assert 'Do not add issue type labels - bug, feature, task.' in text, "expected to find: " + 'Do not add issue type labels - bug, feature, task.'[:80]

