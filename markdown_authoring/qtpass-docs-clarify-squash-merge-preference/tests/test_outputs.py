"""Behavioral checks for qtpass-docs-clarify-squash-merge-preference (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert '**Avoid force pushing to shared branches** - Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Never force push to main or branches ' in text, "expected to find: " + '**Avoid force pushing to shared branches** - Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Never force push to main or branches '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'Squash merging keeps the main branch history clean and avoids cluttering it with numerous intermediate commits from review iterations.' in text, "expected to find: " + 'Squash merging keeps the main branch history clean and avoids cluttering it with numerous intermediate commits from review iterations.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'gh pr merge <PR_NUMBER> --squash --auto --delete-branch --subject "fix: description"' in text, "expected to find: " + 'gh pr merge <PR_NUMBER> --squash --auto --delete-branch --subject "fix: description"'[:80]

