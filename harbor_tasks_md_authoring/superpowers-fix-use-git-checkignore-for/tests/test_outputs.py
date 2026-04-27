"""Behavioral checks for superpowers-fix-use-git-checkignore-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/superpowers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/using-git-worktrees/SKILL.md')
    assert 'git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null' in text, "expected to find: " + 'git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/using-git-worktrees/SKILL.md')
    assert '- **Fix:** Always use `git check-ignore` before creating project-local worktree' in text, "expected to find: " + '- **Fix:** Always use `git check-ignore` before creating project-local worktree'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/using-git-worktrees/SKILL.md')
    assert '# Check if directory is ignored (respects local, global, and system gitignore)' in text, "expected to find: " + '# Check if directory is ignored (respects local, global, and system gitignore)'[:80]

