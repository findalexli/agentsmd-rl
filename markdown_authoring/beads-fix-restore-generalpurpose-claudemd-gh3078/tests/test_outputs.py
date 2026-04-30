"""Behavioral checks for beads-fix-restore-generalpurpose-claudemd-gh3078 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/beads")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**Remember**: We're building this tool to help AI agents like you! If you find the workflow confusing or have ideas for improvement, create an issue with your feedback." in text, "expected to find: " + "**Remember**: We're building this tool to help AI agents like you! If you find the workflow confusing or have ideas for improvement, create an issue with your feedback."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is **beads** (command: `bd`), an issue tracker designed for AI-supervised coding workflows. We dogfood our own tool!' in text, "expected to find: " + 'This is **beads** (command: `bd`), an issue tracker designed for AI-supervised coding workflows. We dogfood our own tool!'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When adding CLI output features, follow these design principles for consistent, cognitively-friendly visuals.' in text, "expected to find: " + 'When adding CLI output features, follow these design principles for consistent, cognitively-friendly visuals.'[:80]

