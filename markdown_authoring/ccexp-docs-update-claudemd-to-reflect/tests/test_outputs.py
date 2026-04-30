"""Behavioral checks for ccexp-docs-update-claudemd-to-reflect (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ccexp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**ccexp** (short for claude-code-explorer) - React Ink-based CLI tool for exploring and managing Claude Code settings and slash commands. The tool provides an interactive terminal UI for file navigati' in text, "expected to find: " + '**ccexp** (short for claude-code-explorer) - React Ink-based CLI tool for exploring and managing Claude Code settings and slash commands. The tool provides an interactive terminal UI for file navigati'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The project employs a sophisticated testing strategy using `fs-fixture` for creating isolated file system environments:' in text, "expected to find: " + 'The project employs a sophisticated testing strategy using `fs-fixture` for creating isolated file system environments:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All jobs run in parallel for efficiency, with PR preview packages only published after all checks pass.' in text, "expected to find: " + 'All jobs run in parallel for efficiency, with PR preview packages only published after all checks pass.'[:80]

