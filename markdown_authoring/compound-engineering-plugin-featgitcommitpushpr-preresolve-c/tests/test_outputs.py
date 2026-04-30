"""Behavioral checks for compound-engineering-plugin-featgitcommitpushpr-preresolve-c (markdown_authoring task).

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
    assert "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== " in text, "expected to find: " + "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing and pushing. Ask whether to create a feature branch' in text, "expected to find: " + 'If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing and pushing. Ask whether to create a feature branch'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Ask the user to confirm: "Update the PR description for this branch?" Use the platform\'s blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini).' in text, "expected to find: " + 'Ask the user to confirm: "Update the PR description for this branch?" Use the platform\'s blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert 'If the current branch from the context above is `main`, `master`, or the resolved default branch from Step 1, warn the user and ask whether to continue committing here or create a feature branch first' in text, "expected to find: " + 'If the current branch from the context above is `main`, `master`, or the resolved default branch from Step 1, warn the user and ask whether to continue committing here or create a feature branch first'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert 'If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing if the user wants this work attached to a branch. A' in text, "expected to find: " + 'If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing if the user wants this work attached to a branch. A'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit/SKILL.md')
    assert "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== " in text, "expected to find: " + "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== "[:80]

