"""Behavioral checks for plannotator-feat-add-reviewrenovate-agent-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/plannotator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-renovate/SKILL.md')
    assert 'description: Review Renovate bot PRs that update GitHub Actions dependencies. Verifies supply chain integrity by checking pinned commit SHAs against upstream tagged releases, reviews changelogs for br' in text, "expected to find: " + 'description: Review Renovate bot PRs that update GitHub Actions dependencies. Verifies supply chain integrity by checking pinned commit SHAs against upstream tagged releases, reviews changelogs for br'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-renovate/SKILL.md')
    assert "You are reviewing a Renovate bot PR that updates GitHub Actions dependencies. Your job is to verify supply chain integrity and ensure the upgrades won't break CI/CD workflows." in text, "expected to find: " + "You are reviewing a Renovate bot PR that updates GitHub Actions dependencies. Your job is to verify supply chain integrity and ensure the upgrades won't break CI/CD workflows."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-renovate/SKILL.md')
    assert 'Compare each result against the SHA in the workflow file. If any SHA does not match, **stop and report a supply chain integrity failure**. Do not approve the PR.' in text, "expected to find: " + 'Compare each result against the SHA in the workflow file. If any SHA does not match, **stop and report a supply chain integrity failure**. Do not approve the PR.'[:80]

