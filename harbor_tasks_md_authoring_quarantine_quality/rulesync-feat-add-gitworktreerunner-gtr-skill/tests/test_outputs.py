"""Behavioral checks for rulesync-feat-add-gitworktreerunner-gtr-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rulesync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/git-worktree-runner/SKILL.md')
    assert 'git-worktree-runner (gtr) is a CLI tool that wraps `git worktree` with quality-of-life features for modern development workflows including editor and AI tool integration.' in text, "expected to find: " + 'git-worktree-runner (gtr) is a CLI tool that wraps `git worktree` with quality-of-life features for modern development workflows including editor and AI tool integration.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/git-worktree-runner/SKILL.md')
    assert 'Manages git worktrees using git-worktree-runner (gtr). Use when the user needs' in text, "expected to find: " + 'Manages git worktrees using git-worktree-runner (gtr). Use when the user needs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/git-worktree-runner/SKILL.md')
    assert 'to create, list, remove, or navigate worktrees with `git gtr` commands, open' in text, "expected to find: " + 'to create, list, remove, or navigate worktrees with `git gtr` commands, open'[:80]

