"""Behavioral checks for quickwit-add-claude-code-skills-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quickwit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bump-tantivy/SKILL.md')
    assert 'gh pr create --title "Bump tantivy to {short-sha}" --body "Updates tantivy dependency to the latest commit on main."' in text, "expected to find: " + 'gh pr create --title "Bump tantivy to {short-sha}" --body "Updates tantivy dependency to the latest commit on main."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bump-tantivy/SKILL.md')
    assert 'Edit `quickwit/Cargo.toml` and update the `rev` field in the tantivy dependency to the new short SHA.' in text, "expected to find: " + 'Edit `quickwit/Cargo.toml` and update the `rev` field in the tantivy dependency to the new short SHA.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bump-tantivy/SKILL.md')
    assert 'description: Bump tantivy to the latest commit on main branch, fix compilation issues, and open a PR' in text, "expected to find: " + 'description: Bump tantivy to the latest commit on main branch, fix compilation issues, and open a PR'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/simple-pr/SKILL.md')
    assert 'Verify that all changes have been staged (no unstaged changes). If there are unstaged changes, abort and ask the user to stage their changes first with `git add`.' in text, "expected to find: " + 'Verify that all changes have been staged (no unstaged changes). If there are unstaged changes, abort and ask the user to stage their changes first with `git add`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/simple-pr/SKILL.md')
    assert 'Based on the staged changes, generate a concise commit message (1-2 sentences) that describes the "why" rather than the "what".' in text, "expected to find: " + 'Based on the staged changes, generate a concise commit message (1-2 sentences) that describes the "why" rather than the "what".'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/simple-pr/SKILL.md')
    assert 'Create a short, descriptive branch name based on the changes (e.g., `fix-typo-in-readme`, `add-retry-logic`, `update-deps`).' in text, "expected to find: " + 'Create a short, descriptive branch name based on the changes (e.g., `fix-typo-in-readme`, `add-retry-logic`, `update-deps`).'[:80]

