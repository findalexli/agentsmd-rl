"""Behavioral checks for humanlayer-update-subagents-to-use-sonnet (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/humanlayer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/codebase-analyzer.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/codebase-locator.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/codebase-pattern-finder.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/thoughts-analyzer.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/thoughts-locator.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/web-search-researcher.md')
    assert 'model: sonnet' in text, "expected to find: " + 'model: sonnet'[:80]

