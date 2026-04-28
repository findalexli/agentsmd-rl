"""Behavioral checks for xarray-add-github-interaction-guidelines-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xarray")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **NEVER impersonate the user on GitHub** - Do not post comments, create issues, or interact with the xarray GitHub repository unless explicitly instructed' in text, "expected to find: " + '- **NEVER impersonate the user on GitHub** - Do not post comments, create issues, or interact with the xarray GitHub repository unless explicitly instructed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Never post "update" messages, progress reports, or explanatory comments on GitHub issues/PRs unless specifically asked' in text, "expected to find: " + '- Never post "update" messages, progress reports, or explanatory comments on GitHub issues/PRs unless specifically asked'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Always require explicit user direction before creating pull requests or pushing to the xarray GitHub repository' in text, "expected to find: " + '- Always require explicit user direction before creating pull requests or pushing to the xarray GitHub repository'[:80]

