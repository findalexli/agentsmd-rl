"""Behavioral checks for agent-skills-update-fluxcontrollerpatchreleases-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert '`gh api graphql -f query=\'{ repository(owner:"<o>",name:"<r>") { pullRequest(number:<n>) { reviewThreads(first:50) { nodes { id isResolved comments(first:1){nodes{databaseId body}} } } } } }\'`.' in text, "expected to find: " + '`gh api graphql -f query=\'{ repository(owner:"<o>",name:"<r>") { pullRequest(number:<n>) { reviewThreads(first:50) { nodes { id isResolved comments(first:1){nodes{databaseId body}} } } } } }\'`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert 'state=$(gh pr view <num> -R fluxcd/<repo> --json mergeStateStatus,reviewDecision --jq \'.reviewDecision+" "+.mergeStateStatus\')' in text, "expected to find: " + 'state=$(gh pr view <num> -R fluxcd/<repo> --json mergeStateStatus,reviewDecision --jq \'.reviewDecision+" "+.mergeStateStatus\')'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert "`gh api repos/<owner>/<repo>/pulls/<n>/comments/<cid>/replies -f body='Fixed, thanks!'`" in text, "expected to find: " + "`gh api repos/<owner>/<repo>/pulls/<n>/comments/<cid>/replies -f body='Fixed, thanks!'`"[:80]

