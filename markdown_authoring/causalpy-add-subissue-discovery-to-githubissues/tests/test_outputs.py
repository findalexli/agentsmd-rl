"""Behavioral checks for causalpy-add-subissue-discovery-to-githubissues (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/causalpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/issue-evaluation.md')
    assert 'Always check whether an issue has native sub-issues. The `trackedIssues` / `trackedInIssues` GraphQL fields only cover older markdown task-list tracking and will miss native sub-issues.' in text, "expected to find: " + 'Always check whether an issue has native sub-issues. The `trackedIssues` / `trackedInIssues` GraphQL fields only cover older markdown task-list tracking and will miss native sub-issues.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/issue-evaluation.md')
    assert '- Review sub-issues (if any) for work breakdown and progress' in text, "expected to find: " + '- Review sub-issues (if any) for work breakdown and progress'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/issue-evaluation.md')
    assert 'subIssues(first: 50) { nodes { number title state url } }' in text, "expected to find: " + 'subIssues(first: 50) { nodes { number title state url } }'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/parent-child-issues.md')
    assert 'When evaluating an issue that may already have sub-issues, always use the `subIssues` GraphQL field. Do **not** use `trackedIssues` / `trackedInIssues` -- those only cover older markdown task-list tra' in text, "expected to find: " + 'When evaluating an issue that may already have sub-issues, always use the `subIssues` GraphQL field. Do **not** use `trackedIssues` / `trackedInIssues` -- those only cover older markdown task-list tra'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/parent-child-issues.md')
    assert 'repository(owner:"<owner>", name:"<repo>") {' in text, "expected to find: " + 'repository(owner:"<owner>", name:"<repo>") {'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/github-issues/reference/parent-child-issues.md')
    assert '## 7) Verify links rendered correctly' in text, "expected to find: " + '## 7) Verify links rendered correctly'[:80]

