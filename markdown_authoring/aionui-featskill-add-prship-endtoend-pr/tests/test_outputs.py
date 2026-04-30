"""Behavioral checks for aionui-featskill-add-prship-endtoend-pr (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-ship/SKILL.md')
    assert '--jq \'[.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED") | select(.name | test("^codecov/") | not) | .name] | join(", ")\')' in text, "expected to find: " + '--jq \'[.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED") | select(.name | test("^codecov/") | not) | .name] | join(", ")\')'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-ship/SKILL.md')
    assert "- **Worktree path** — always `/tmp/aionui-ship-<PR_NUMBER>` (distinct from pr-automation's `/tmp/aionui-pr-*` and pr-verify's `/tmp/aionui-verify-*`)" in text, "expected to find: " + "- **Worktree path** — always `/tmp/aionui-ship-<PR_NUMBER>` (distinct from pr-automation's `/tmp/aionui-pr-*` and pr-verify's `/tmp/aionui-verify-*`)"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-ship/SKILL.md')
    assert 'Fix only CI-reported errors (lint errors, type errors, test failures) in the worktree. No refactoring, no scope expansion.' in text, "expected to find: " + 'Fix only CI-reported errors (lint errors, type errors, test failures) in the worktree. No refactoring, no scope expansion.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **pr-ship**       | End-to-end PR lifecycle: create, CI wait, review, fix, merge in one invocation        | `/pr-ship`, after development is done, resume shepherding a PR            |' in text, "expected to find: " + '| **pr-ship**       | End-to-end PR lifecycle: create, CI wait, review, fix, merge in one invocation        | `/pr-ship`, after development is done, resume shepherding a PR            |'[:80]

