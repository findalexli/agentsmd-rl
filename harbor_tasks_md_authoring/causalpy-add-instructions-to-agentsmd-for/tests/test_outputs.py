"""Behavioral checks for causalpy-add-instructions-to-agentsmd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/causalpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **User review**: Always present the draft issue to the user for review before filing. The user should have the opportunity to view, modify, or approve the issue content before it is submitted.' in text, "expected to find: " + '2. **User review**: Always present the draft issue to the user for review before filing. The user should have the opportunity to view, modify, or approve the issue content before it is submitted.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When you or the user identify an issue (bug, enhancement, or task), you can automatically create a GitHub issue using the GitHub CLI.' in text, "expected to find: " + 'When you or the user identify an issue (bug, enhancement, or task), you can automatically create a GitHub issue using the GitHub CLI.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Authenticate**: Run `gh auth login` and follow the prompts to authorize access to the repository.' in text, "expected to find: " + '- **Authenticate**: Run `gh auth login` and follow the prompts to authorize access to the repository.'[:80]

