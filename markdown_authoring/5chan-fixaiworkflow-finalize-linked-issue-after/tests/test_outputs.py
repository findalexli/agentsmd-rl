"""Behavioral checks for 5chan-fixaiworkflow-finalize-linked-issue-after (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/5chan")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/review-and-merge-pr/SKILL.md')
    assert 'description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the ' in text, "expected to find: " + 'description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/review-and-merge-pr/SKILL.md')
    assert "ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')" in text, "expected to find: " + "ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/review-and-merge-pr/SKILL.md')
    assert 'ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)' in text, "expected to find: " + 'ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/review-and-merge-pr/SKILL.md')
    assert 'description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the ' in text, "expected to find: " + 'description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/review-and-merge-pr/SKILL.md')
    assert "ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')" in text, "expected to find: " + "ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/review-and-merge-pr/SKILL.md')
    assert 'ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)' in text, "expected to find: " + 'ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)'[:80]

