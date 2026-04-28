"""Behavioral checks for opendal-docs-require-following-pr-template (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opendal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Always follow OpenDAL's pull request template when creating a PR." in text, "expected to find: " + "- Always follow OpenDAL's pull request template when creating a PR."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## Pull Request Requirements' in text, "expected to find: " + '## Pull Request Requirements'[:80]

