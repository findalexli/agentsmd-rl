"""Behavioral checks for wvlet-doc-add-github-cli-commands (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wvlet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`' in text, "expected to find: " + '- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- To debug SQL generator, add -L *GenSQL=trace to the test option' in text, "expected to find: " + '- To debug SQL generator, add -L *GenSQL=trace to the test option'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- View PR checks: `gh pr checks PR_NUMBER`' in text, "expected to find: " + '- View PR checks: `gh pr checks PR_NUMBER`'[:80]

