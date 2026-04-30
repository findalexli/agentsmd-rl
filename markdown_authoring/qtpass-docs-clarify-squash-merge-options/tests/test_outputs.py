"""Behavioral checks for qtpass-docs-clarify-squash-merge-options (markdown_authoring task).

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
    assert 'Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Prefer `--force-with-lease` over `-f` because it fails if someone else pushed to t' in text, "expected to find: " + 'Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Prefer `--force-with-lease` over `-f` because it fails if someone else pushed to t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'gh pr merge <PR_NUMBER> --squash --delete-branch --subject "fix: description"' in text, "expected to find: " + 'gh pr merge <PR_NUMBER> --squash --delete-branch --subject "fix: description"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'Never force push to main or branches that others may be working from.' in text, "expected to find: " + 'Never force push to main or branches that others may be working from.'[:80]

