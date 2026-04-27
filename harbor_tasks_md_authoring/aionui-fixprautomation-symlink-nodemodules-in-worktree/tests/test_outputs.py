"""Behavioral checks for aionui-fixprautomation-symlink-nodemodules-in-worktree (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"' in text, "expected to find: " + 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert '# Symlink node_modules so tsc/lint can run in the worktree' in text, "expected to find: " + '# Symlink node_modules so tsc/lint can run in the worktree'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert 'After creating the worktree (all three paths), symlink `node_modules` so lint/tsc/test can run:' in text, "expected to find: " + 'After creating the worktree (all three paths), symlink `node_modules` so lint/tsc/test can run:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"' in text, "expected to find: " + 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '# Symlink node_modules so lint/tsc/test can run in the worktree' in text, "expected to find: " + '# Symlink node_modules so lint/tsc/test can run in the worktree'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"' in text, "expected to find: " + 'ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"'[:80]

