"""Behavioral checks for surrealdb-add-cursor-rule-for-git (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/surrealdb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-safety.mdc')
    assert '- When formatting or linting produces changes after a commit, create a new follow-up commit (e.g. "Format code") rather than amending.' in text, "expected to find: " + '- When formatting or linting produces changes after a commit, create a new follow-up commit (e.g. "Format code") rather than amending.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-safety.mdc')
    assert '- Never amend a commit that has already been pushed to a remote, unless specifically requested. Always create a new commit instead.' in text, "expected to find: " + '- Never amend a commit that has already been pushed to a remote, unless specifically requested. Always create a new commit instead.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-safety.mdc')
    assert '- Never run destructive or irreversible git commands (hard reset, branch deletion, etc.) unless explicitly requested.' in text, "expected to find: " + '- Never run destructive or irreversible git commands (hard reset, branch deletion, etc.) unless explicitly requested.'[:80]

