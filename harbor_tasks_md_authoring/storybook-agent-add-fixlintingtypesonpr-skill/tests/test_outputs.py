"""Behavioral checks for storybook-agent-add-fixlintingtypesonpr-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/storybook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-linting-types-on-pr/SKILL.md')
    assert 'description: Checks out a PR (including fork PRs), fixes all linting and TypeScript errors, then pushes the changes back. Use when asked to fix lint, types, or TS errors on a PR.' in text, "expected to find: " + 'description: Checks out a PR (including fork PRs), fixes all linting and TypeScript errors, then pushes the changes back. Use when asked to fix lint, types, or TS errors on a PR.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-linting-types-on-pr/SKILL.md')
    assert '- If `gh pr checkout` fails due to permissions on a fork, inform the user — they may need to grant write access to the fork or the maintainer must push directly.' in text, "expected to find: " + '- If `gh pr checkout` fails due to permissions on a fork, inform the user — they may need to grant write access to the fork or the maintainer must push directly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-linting-types-on-pr/SKILL.md')
    assert 'This automatically sets up the correct remote tracking and switches to the PR branch, even when the PR comes from a fork.' in text, "expected to find: " + 'This automatically sets up the correct remote tracking and switches to the PR branch, even when the PR comes from a fork.'[:80]

