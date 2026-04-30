"""Behavioral checks for spawn-feat-add-git-worktree-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-trigger-service/SKILL.md')
    assert "When multiple agents work in parallel, they MUST use worktrees instead of `git checkout -b` to avoid clobbering each other's uncommitted changes:" in text, "expected to find: " + "When multiple agents work in parallel, they MUST use worktrees instead of `git checkout -b` to avoid clobbering each other's uncommitted changes:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-trigger-service/SKILL.md')
    assert 'These conventions are already embedded in the prompts of `improve.sh` and `refactor.sh`. When adding new service scripts, copy the same patterns.' in text, "expected to find: " + 'These conventions are already embedded in the prompts of `improve.sh` and `refactor.sh`. When adding new service scripts, copy the same patterns.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-trigger-service/SKILL.md')
    assert 'All agent team scripts (`improve.sh`, `refactor.sh`, and any future scripts) MUST instruct their agents to follow these conventions:' in text, "expected to find: " + 'All agent team scripts (`improve.sh`, `refactor.sh`, and any future scripts) MUST instruct their agents to follow these conventions:'[:80]

