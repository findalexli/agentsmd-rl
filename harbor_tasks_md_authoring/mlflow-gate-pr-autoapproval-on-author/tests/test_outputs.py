"""Behavioral checks for mlflow-gate-pr-autoapproval-on-author (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mlflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '- Otherwise (including API errors, e.g., 404 for non-collaborators) -> do NOT approve. Do not mention the reason for not approving in the review.' in text, "expected to find: " + '- Otherwise (including API errors, e.g., 404 for non-collaborators) -> do NOT approve. Do not mention the reason for not approving in the review.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'Approve the PR when there are no issues or only minor issues, but **only if the PR author has the `admin` or `maintain` role**.' in text, "expected to find: " + 'Approve the PR when there are no issues or only minor issues, but **only if the PR author has the `admin` or `maintain` role**.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'gh api repos/<owner>/<repo>/collaborators/"$author"/permission --jq \'.role_name\'' in text, "expected to find: " + 'gh api repos/<owner>/<repo>/collaborators/"$author"/permission --jq \'.role_name\''[:80]

