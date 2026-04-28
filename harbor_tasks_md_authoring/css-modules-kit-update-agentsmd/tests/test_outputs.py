"""Behavioral checks for css-modules-kit-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/css-modules-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `<type>` is one of: feat, fix, docs, refactor, test, chore, deps' in text, "expected to find: " + '- `<type>` is one of: feat, fix, docs, refactor, test, chore, deps'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Write PR descriptions and commit messages in English' in text, "expected to find: " + '- Write PR descriptions and commit messages in English'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `Type: Testing`: Test additions/modifications' in text, "expected to find: " + '- `Type: Testing`: Test additions/modifications'[:80]

