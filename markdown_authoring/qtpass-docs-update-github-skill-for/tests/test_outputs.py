"""Behavioral checks for qtpass-docs-update-github-skill-for (markdown_authoring task).

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
    assert 'gh api graphql -f query=\'{ repository(owner: "<OWNER>", name: "<REPO>") { pullRequest(number: <PR_NUMBER>) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }\' | jq -r \'.data.repository.pu' in text, "expected to find: " + 'gh api graphql -f query=\'{ repository(owner: "<OWNER>", name: "<REPO>") { pullRequest(number: <PR_NUMBER>) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }\' | jq -r \'.data.repository.pu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'gh api "repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"' in text, "expected to find: " + 'gh api "repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"'[:80]

