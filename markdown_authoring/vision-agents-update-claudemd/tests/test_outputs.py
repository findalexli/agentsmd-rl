"""Behavioral checks for vision-agents-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vision-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Don\'t add error handling, logging, validation, comments, abstractions, config options, or "future-proofing" I didn\'t' in text, "expected to find: " + '- Don\'t add error handling, logging, validation, comments, abstractions, config options, or "future-proofing" I didn\'t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Match the style and abstraction level of surrounding code. Don't introduce new patterns or helpers unless asked." in text, "expected to find: " + "- Match the style and abstraction level of surrounding code. Don't introduce new patterns or helpers unless asked."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Change only what I asked for. Don't refactor adjacent code — ask first." in text, "expected to find: " + "- Change only what I asked for. Don't refactor adjacent code — ask first."[:80]

