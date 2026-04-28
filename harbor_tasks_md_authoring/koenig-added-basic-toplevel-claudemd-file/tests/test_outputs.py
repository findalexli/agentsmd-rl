"""Behavioral checks for koenig-added-basic-toplevel-claudemd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/koenig")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Koenig is Ghost's editor based on the Lexical framework. This is a Lerna-managed monorepo containing multiple packages for Ghost's content editing ecosystem." in text, "expected to find: " + "Koenig is Ghost's editor based on the Lexical framework. This is a Lerna-managed monorepo containing multiple packages for Ghost's content editing ecosystem."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **[koenig-lexical](packages/koenig-lexical)**: Main editor package - React components built on Lexical' in text, "expected to find: " + '- **[koenig-lexical](packages/koenig-lexical)**: Main editor package - React components built on Lexical'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **[kg-lexical-html-renderer](packages/kg-lexical-html-renderer)**: Converts serialized Lexical to HTML' in text, "expected to find: " + '- **[kg-lexical-html-renderer](packages/kg-lexical-html-renderer)**: Converts serialized Lexical to HTML'[:80]

