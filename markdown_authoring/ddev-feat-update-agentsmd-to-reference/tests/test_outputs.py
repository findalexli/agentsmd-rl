"""Behavioral checks for ddev-feat-update-agentsmd-to-reference (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ddev")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For standard DDEV organization patterns including communication style, branch naming, PR creation, and common development practices, see the [organization-wide AGENTS.md](https://github.com/ddev/.gith' in text, "expected to find: " + 'For standard DDEV organization patterns including communication style, branch naming, PR creation, and common development practices, see the [organization-wide AGENTS.md](https://github.com/ddev/.gith'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides guidance to AI agents when working with the DDEV core codebase.' in text, "expected to find: " + 'This file provides guidance to AI agents when working with the DDEV core codebase.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## General DDEV Development Patterns' in text, "expected to find: " + '## General DDEV Development Patterns'[:80]

