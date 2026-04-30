"""Behavioral checks for kaos-featskills-add-dependabotfix-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kaos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert 'description: Systematically diagnose and fix a failing Dependabot PR. Use this skill when asked to run /dependabot-fix <pr-number>. The user provides the PR number in their prompt. The skill fetches P' in text, "expected to find: " + 'description: Systematically diagnose and fix a failing Dependabot PR. Use this skill when asked to run /dependabot-fix <pr-number>. The user provides the PR number in their prompt. The skill fetches P'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert '| `requires go >= X.Y.Z (running go A.B.C)` | Unpinned `@latest` tool install pulled newer version requiring bumped toolchain | Pin to last version compatible with current `go.mod` |' in text, "expected to find: " + '| `requires go >= X.Y.Z (running go A.B.C)` | Unpinned `@latest` tool install pulled newer version requiring bumped toolchain | Pin to last version compatible with current `go.mod` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert '| `Node.js X is not supported` | Action bumped requires newer Node runner | Verify runner Node version; revert major if needed |' in text, "expected to find: " + '| `Node.js X is not supported` | Action bumped requires newer Node runner | Verify runner Node version; revert major if needed |'[:80]

