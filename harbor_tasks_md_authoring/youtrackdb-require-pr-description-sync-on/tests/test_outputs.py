"""Behavioral checks for youtrackdb-require-pr-description-sync-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/youtrackdb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Keep the PR title and description in sync with follow-up commits.** The squashed commit message is built from the PR title and description, not from individual commit messages — update them with e' in text, "expected to find: " + '- **Keep the PR title and description in sync with follow-up commits.** The squashed commit message is built from the PR title and description, not from individual commit messages — update them with e'[:80]

