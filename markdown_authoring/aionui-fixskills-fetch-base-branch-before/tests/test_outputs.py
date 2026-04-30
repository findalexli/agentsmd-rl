"""Behavioral checks for aionui-fixskills-fetch-base-branch-before (markdown_authoring task).

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
    assert "# Create worktree on the PR's head branch; fetch base branch for accurate rebase" in text, "expected to find: " + "# Create worktree on the PR's head branch; fetch base branch for accurate rebase"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'git fetch origin <base_branch>' in text, "expected to find: " + 'git fetch origin <base_branch>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'git fetch origin "$BASE_REF"' in text, "expected to find: " + 'git fetch origin "$BASE_REF"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert "BASE_REF=$(gh pr view ${PR_NUMBER} --json baseRefName --jq '.baseRefName')" in text, "expected to find: " + "BASE_REF=$(gh pr view ${PR_NUMBER} --json baseRefName --jq '.baseRefName')"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '# Fetch PR head AND base branch so the three-dot diff is accurate' in text, "expected to find: " + '# Fetch PR head AND base branch so the three-dot diff is accurate'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'git fetch origin "$BASE_REF"' in text, "expected to find: " + 'git fetch origin "$BASE_REF"'[:80]

