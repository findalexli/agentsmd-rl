"""Behavioral checks for claude-code-statusline-docs-update-claude-code-compatibility (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-statusline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location' in text, "expected to find: " + '**Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Architecture**: Single Config.toml (227 settings), modular cache (8 sub-modules), 91.5% code reduction' in text, "expected to find: " + '**Architecture**: Single Config.toml (227 settings), modular cache (8 sub-modules), 91.5% code reduction'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Current**: v2.17.0 | **Claude Code**: v2.1.6–v2.1.19 ✓ | **Branch**: dev → nightly → main' in text, "expected to find: " + '**Current**: v2.17.0 | **Claude Code**: v2.1.6–v2.1.19 ✓ | **Branch**: dev → nightly → main'[:80]

