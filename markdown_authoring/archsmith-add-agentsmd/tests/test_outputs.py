"""Behavioral checks for archsmith-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/archsmith")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do NOT append `Co-Authored-By` lines to commit messages.' in text, "expected to find: " + '- Do NOT append `Co-Authored-By` lines to commit messages.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## Git Commit Rules' in text, "expected to find: " + '## Git Commit Rules'[:80]

