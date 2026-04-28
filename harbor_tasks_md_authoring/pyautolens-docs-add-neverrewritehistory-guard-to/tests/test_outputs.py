"""Behavioral checks for pyautolens-docs-add-neverrewritehistory-guard-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pyautolens")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'and any other agent. The "Initial commit — fresh start for AI workflow" pattern' in text, "expected to find: " + 'and any other agent. The "Initial commit — fresh start for AI workflow" pattern'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This applies equally to humans, local Claude Code, cloud Claude agents, Codex,' in text, "expected to find: " + 'This applies equally to humans, local Claude Code, cloud Claude agents, Codex,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'exactly what this rule prevents — it costs ~40 commits of redundant local work' in text, "expected to find: " + 'exactly what this rule prevents — it costs ~40 commits of redundant local work'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'and any other agent. The "Initial commit — fresh start for AI workflow" pattern' in text, "expected to find: " + 'and any other agent. The "Initial commit — fresh start for AI workflow" pattern'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This applies equally to humans, local Claude Code, cloud Claude agents, Codex,' in text, "expected to find: " + 'This applies equally to humans, local Claude Code, cloud Claude agents, Codex,'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'exactly what this rule prevents — it costs ~40 commits of redundant local work' in text, "expected to find: " + 'exactly what this rule prevents — it costs ~40 commits of redundant local work'[:80]

