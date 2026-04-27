"""Behavioral checks for cc-skills-featconventionalgit-add-worktree-naming-convention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cc-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/conventional-git/SKILL.md')
    assert 'description: Conventional Commits v1.0.0 branch naming, worktree naming, and commit message standards for GitHub and GitLab projects. Use when creating branches, naming worktrees, writing commits, gen' in text, "expected to find: " + 'description: Conventional Commits v1.0.0 branch naming, worktree naming, and commit message standards for GitHub and GitLab projects. Use when creating branches, naming worktrees, writing commits, gen'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/conventional-git/SKILL.md')
    assert 'The directory name mirrors the branch name so `git worktree list` stays readable and each worktree is immediately traceable to its branch without inspecting the checkout. Run `git worktree list` befor' in text, "expected to find: " + 'The directory name mirrors the branch name so `git worktree list` stays readable and each worktree is immediately traceable to its branch without inspecting the checkout. Run `git worktree list` befor'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/conventional-git/SKILL.md')
    assert 'Remove the worktree once its branch is merged — either after a local merge or after the pull/merge request is closed on the remote. Stale worktrees accumulate and make `git worktree list` unreadable.' in text, "expected to find: " + 'Remove the worktree once its branch is merged — either after a local merge or after the pull/merge request is closed on the remote. Stale worktrees accumulate and make `git worktree list` unreadable.'[:80]

