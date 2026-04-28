"""Behavioral checks for dune-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dune")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `otherlibs` - public libraries that live in this repository. not necessarily dune related' in text, "expected to find: " + '- `otherlibs` - public libraries that live in this repository. not necessarily dune related'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'make fmt                   # Auto-format code (always run before committing)' in text, "expected to find: " + 'make fmt                   # Auto-format code (always run before committing)'[:80]

