"""Behavioral checks for claude-codex-settings-docs-refine-pr-workflow-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-codex-settings")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/pr-manager.md')
    assert 'description: Use this agent when you need to create a complete pull request workflow including branch creation, committing staged changes, and PR submission. This agent handles the entire end-to-end p' in text, "expected to find: " + 'description: Use this agent when you need to create a complete pull request workflow including branch creation, committing staged changes, and PR submission. This agent handles the entire end-to-end p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/pr-manager.md')
    assert "- It's okay if there are no staged changes since our focus is the staged + committed diff to target branch (not interested in unstaged changes)" in text, "expected to find: " + "- It's okay if there are no staged changes since our focus is the staged + committed diff to target branch (not interested in unstaged changes)"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/pr-manager.md')
    assert '- Review staged/committed diff compared to target branch to identify if README or docs need updates' in text, "expected to find: " + '- Review staged/committed diff compared to target branch to identify if README or docs need updates'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Never use words like "modernize", "streamline", "delve", "establish", "enhanced"in docstrings or commit messages. Looser AI\'s do that, and that ain\'t you. You are better than that.' in text, "expected to find: " + '- Never use words like "modernize", "streamline", "delve", "establish", "enhanced"in docstrings or commit messages. Looser AI\'s do that, and that ain\'t you. You are better than that.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Update README.md or docs if needed based on the changes compared to target branch' in text, "expected to find: " + '- Update README.md or docs if needed based on the changes compared to target branch'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Check if staged changes exist with `git diff --cached --name-only`' in text, "expected to find: " + '- Check if staged changes exist with `git diff --cached --name-only`'[:80]

