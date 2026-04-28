"""Behavioral checks for qtpass-docs-potential-fixes-for-3 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert '# Fetch (via pull) and rebase on main' in text, "expected to find: " + '# Fetch (via pull) and rebase on main'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert '# Checkout, fetch, and rebase' in text, "expected to find: " + '# Checkout, fetch, and rebase'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'git fetch upstream' in text, "expected to find: " + 'git fetch upstream'[:80]

