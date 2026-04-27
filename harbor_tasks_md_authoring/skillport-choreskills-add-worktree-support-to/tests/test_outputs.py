"""Behavioral checks for skillport-choreskills-add-worktree-support-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skillport")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/experimental/git-branch-cleanup/SKILL.md')
    assert 'compatibility: Requires git 2.17+ (for worktree support). Git 2.22+ recommended for `git branch --show-current`.' in text, "expected to find: " + 'compatibility: Requires git 2.17+ (for worktree support). Git 2.22+ recommended for `git branch --show-current`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/experimental/git-branch-cleanup/SKILL.md')
    assert '| **Has Worktree** | Branch checked out in a worktree (`+` prefix in `git branch -v`) | Remove worktree first |' in text, "expected to find: " + '| **Has Worktree** | Branch checked out in a worktree (`+` prefix in `git branch -v`) | Remove worktree first |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/experimental/git-branch-cleanup/SKILL.md')
    assert "git branch -v | grep '\\[gone\\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do" in text, "expected to find: " + "git branch -v | grep '\\[gone\\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do"[:80]

