"""Behavioral checks for openhands-infra-docsskill-add-git-worktree-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openhands-infra")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert '**Use git worktrees** to work on features, bug fixes, docs, or any git commits/PRs in an isolated workspace without affecting the current branch.' in text, "expected to find: " + '**Use git worktrees** to work on features, bug fixes, docs, or any git commits/PRs in an isolated workspace without affecting the current branch.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert '**Important**: The shared `.venv/` (Python) lives in the main repo. Run Python tests with the full path:' in text, "expected to find: " + '**Important**: The shared `.venv/` (Python) lives in the main repo. Run Python tests with the full path:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert 'Branch naming: `feat/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`' in text, "expected to find: " + 'Branch naming: `feat/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`'[:80]

