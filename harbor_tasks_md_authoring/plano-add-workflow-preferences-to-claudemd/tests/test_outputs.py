"""Behavioral checks for plano-add-workflow-preferences-to-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/plano")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Git commits:** Do NOT add `Co-Authored-By` lines. Keep commit messages short and concise (one line, no verbose descriptions). NEVER commit and push directly to `main`—always use a feature branch a' in text, "expected to find: " + '- **Git commits:** Do NOT add `Co-Authored-By` lines. Keep commit messages short and concise (one line, no verbose descriptions). NEVER commit and push directly to `main`—always use a feature branch a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **GitHub issues:** When a GitHub issue URL is pasted, fetch all requirements and context from the issue first. The end goal is always a PR with all tests passing.' in text, "expected to find: " + '- **GitHub issues:** When a GitHub issue URL is pasted, fetch all requirements and context from the issue first. The end goal is always a PR with all tests passing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Git branches:** Use the format `<github_username>/<feature_name>` when creating branches for PRs. Determine the username from `gh api user --jq .login`.' in text, "expected to find: " + '- **Git branches:** Use the format `<github_username>/<feature_name>` when creating branches for PRs. Determine the username from `gh api user --jq .login`.'[:80]

