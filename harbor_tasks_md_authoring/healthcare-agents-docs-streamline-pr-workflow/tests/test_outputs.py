"""Behavioral checks for healthcare-agents-docs-streamline-pr-workflow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/healthcare-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not merge the feature branch into local `main` before opening or merging the PR. That creates duplicate local merge commits and makes `main` appear ahead/behind after GitHub merges the PR.' in text, "expected to find: " + '- Do not merge the feature branch into local `main` before opening or merging the PR. That creates duplicate local merge commits and makes `main` appear ahead/behind after GitHub merges the PR.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For docs-only or metadata-only changes, the streamlined path is: branch -> commit -> push branch -> `gh pr create` -> `gh pr merge --merge --delete-branch` -> sync local `main`.' in text, "expected to find: " + '- For docs-only or metadata-only changes, the streamlined path is: branch -> commit -> push branch -> `gh pr create` -> `gh pr merge --merge --delete-branch` -> sync local `main`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For requested edits, create a short-lived branch, commit there, push the branch, open a PR, and merge the PR with `gh pr merge`.' in text, "expected to find: " + '- For requested edits, create a short-lived branch, commit there, push the branch, open a PR, and merge the PR with `gh pr merge`.'[:80]

