"""Behavioral checks for gitea-update-agentsmd-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gitea")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always start issue and pull request comments with an authorship attribution' in text, "expected to find: " + '- Always start issue and pull request comments with an authorship attribution'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Never force-push to pull request branches' in text, "expected to find: " + '- Never force-push to pull request branches'[:80]

