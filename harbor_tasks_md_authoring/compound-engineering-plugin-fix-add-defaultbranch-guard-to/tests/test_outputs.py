"""Behavioral checks for compound-engineering-plugin-fix-add-defaultbranch-guard-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '1. If on `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first (`command git checkout -b <branch-name>`). Derive the branch name from the change conte' in text, "expected to find: " + '1. If on `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first (`command git checkout -b <branch-name>`). Derive the branch name from the change conte'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:' in text, "expected to find: " + 'The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert "command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'" in text, "expected to find: " + "command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert "If the current branch matches `main`, `master`, or the resolved default branch name, warn the user and ask whether to continue committing here or create a feature branch first. Use the platform's bloc" in text, "expected to find: " + "If the current branch matches `main`, `master`, or the resolved default branch name, warn the user and ask whether to continue committing here or create a feature branch first. Use the platform's bloc"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert 'The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:' in text, "expected to find: " + 'The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert "command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'" in text, "expected to find: " + "command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'"[:80]

