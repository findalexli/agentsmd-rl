"""Behavioral checks for rulesync-featskills-add-fork-pr-checkout (markdown_authoring task).

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
    assert '- **"refusing to fetch into branch checked out at..."**: A worktree with that branch exists. `git gtr rm <branch>` first.' in text, "expected to find: " + '- **"refusing to fetch into branch checked out at..."**: A worktree with that branch exists. `git gtr rm <branch>` first.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/git-worktree-runner/SKILL.md')
    assert "For PRs from forked repositories, the branch is not on `origin`. Use GitHub's `refs/pull/<number>/head` ref to fetch it." in text, "expected to find: " + "For PRs from forked repositories, the branch is not on `origin`. Use GitHub's `refs/pull/<number>/head` ref to fetch it."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/git-worktree-runner/SKILL.md')
    assert '3. **Fetch the PR ref** into a local branch (use `--force` to handle diverged history from force-pushes)' in text, "expected to find: " + '3. **Fetch the PR ref** into a local branch (use `--force` to handle diverged history from force-pushes)'[:80]

