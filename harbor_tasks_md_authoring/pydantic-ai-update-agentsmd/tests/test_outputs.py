"""Behavioral checks for pydantic-ai-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pydantic-ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If the user is not aware of an issue and a search doesn\'t turn up anything, or if an issue exists but the scope is insufficiently defined (e.g. there\'s no "obvious" solution and no maintainer input on' in text, "expected to find: " + 'If the user is not aware of an issue and a search doesn\'t turn up anything, or if an issue exists but the scope is insufficiently defined (e.g. there\'s no "obvious" solution and no maintainer input on'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "As such, we prefer strong primitives, powerful abstractions, and general solutions and extension points that enable people to build things that we hadn't even thought of, over narrow solutions for spe" in text, "expected to find: " + "As such, we prefer strong primitives, powerful abstractions, and general solutions and extension points that enable people to build things that we hadn't even thought of, over narrow solutions for spe"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Being an open source library, the public API, abstractions, documentation, and the code itself _are_ the product and deserve careful consideration, as much as the functionality the library or any give' in text, "expected to find: " + 'Being an open source library, the public API, abstractions, documentation, and the code itself _are_ the product and deserve careful consideration, as much as the functionality the library or any give'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

