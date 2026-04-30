"""Behavioral checks for milady-docs-ensure-trailing-newline-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/milady")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The principle: **every change must end up as a commit on the current branch in the current worktree, and ideally pushed.** No stashes, no branch hopping, no work that exists only in the working tree o' in text, "expected to find: " + 'The principle: **every change must end up as a commit on the current branch in the current worktree, and ideally pushed.** No stashes, no branch hopping, no work that exists only in the working tree o'[:80]

