"""Behavioral checks for go-git-add-githubcopilotinstructionsmd-with-pr-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/go-git")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When reviewing pull requests in this repository, focus on correctness, maintainability, test quality, and compatibility with upstream Git behavior.' in text, "expected to find: " + 'When reviewing pull requests in this repository, focus on correctness, maintainability, test quality, and compatibility with upstream Git behavior.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Flag APIs that use unclear names, unnecessary abstractions, non-idiomatic error handling, avoidable global state, or surprising behavior.' in text, "expected to find: " + '- Flag APIs that use unclear names, unnecessary abstractions, non-idiomatic error handling, avoidable global state, or surprising behavior.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Watch for files added in one commit and removed in a later commit within the same PR, since they still enter the repository history.' in text, "expected to find: " + '- Watch for files added in one commit and removed in a later commit within the same PR, since they still enter the repository history.'[:80]

