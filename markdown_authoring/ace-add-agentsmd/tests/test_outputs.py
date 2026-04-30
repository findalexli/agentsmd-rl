"""Behavioral checks for ace-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ace")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ace-context.mdc')
    assert '.cursor/rules/ace-context.mdc' in text, "expected to find: " + '.cursor/rules/ace-context.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-rereview.mdc')
    assert '.cursor/rules/pr-rereview.mdc' in text, "expected to find: " + '.cursor/rules/pr-rereview.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-review.mdc')
    assert '.cursor/rules/pr-review.mdc' in text, "expected to find: " + '.cursor/rules/pr-review.mdc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'To use the PR review rules, configure the GitHub MCP server in Cursor\'s "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, C' in text, "expected to find: " + 'To use the PR review rules, configure the GitHub MCP server in Cursor\'s "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, C'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For re-reviews, classify prior comments as **Addressed**, **Partially Addressed**, **Unaddressed**, or **Dismissed**. Treat clear author rationale as addressed when appropriate.' in text, "expected to find: " + 'For re-reviews, classify prior comments as **Addressed**, **Partially Addressed**, **Unaddressed**, or **Dismissed**. Treat clear author rationale as addressed when appropriate.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When running tests in a conda environment, use `python -m pytest` (not `pytest`) to ensure the correct interpreter is used.' in text, "expected to find: " + 'When running tests in a conda environment, use `python -m pytest` (not `pytest`) to ensure the correct interpreter is used.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

