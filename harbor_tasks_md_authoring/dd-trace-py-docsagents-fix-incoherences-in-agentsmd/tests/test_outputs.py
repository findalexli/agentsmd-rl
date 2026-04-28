"""Behavioral checks for dd-trace-py-docsagents-fix-incoherences-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dd-trace-py")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Purpose:** Creates or updates release notes using Reno, following dd-trace-py's conventions:" in text, "expected to find: " + "**Purpose:** Creates or updates release notes using Reno, following dd-trace-py's conventions:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Use whenever:** Creating or updating release notes for changes in the current branch.' in text, "expected to find: " + '**Use whenever:** Creating or updating release notes for changes in the current branch.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Generates Reno release note files for the current branch changes' in text, "expected to find: " + '- Generates Reno release note files for the current branch changes'[:80]

