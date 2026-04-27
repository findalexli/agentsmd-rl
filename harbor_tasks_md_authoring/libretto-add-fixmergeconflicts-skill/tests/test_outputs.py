"""Behavioral checks for libretto-add-fixmergeconflicts-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-merge-conflicts/SKILL.md')
    assert 'description: Resolve Git merge, rebase, or cherry-pick conflicts by preserving intent from both sides. Use when unmerged paths or conflict markers are present, especially when you must inspect the PR ' in text, "expected to find: " + 'description: Resolve Git merge, rebase, or cherry-pick conflicts by preserving intent from both sides. Use when unmerged paths or conflict markers are present, especially when you must inspect the PR '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-merge-conflicts/SKILL.md')
    assert "-f query='query($owner:String!,$repo:String!,$sha:GitObjectID!){repository(owner:$owner,name:$repo){object(oid:$sha){... on Commit{associatedPullRequests(first:5){nodes{number title body url mergedAt " in text, "expected to find: " + "-f query='query($owner:String!,$repo:String!,$sha:GitObjectID!){repository(owner:$owner,name:$repo){object(oid:$sha){... on Commit{associatedPullRequests(first:5){nodes{number title body url mergedAt "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-merge-conflicts/SKILL.md')
    assert 'If the user chooses one side, preserve that side and salvage any non-conflicting behavior from the other side.' in text, "expected to find: " + 'If the user chooses one side, preserve that side and salvage any non-conflicting behavior from the other side.'[:80]

