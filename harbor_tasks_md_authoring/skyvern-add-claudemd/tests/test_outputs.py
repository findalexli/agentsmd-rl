"""Behavioral checks for skyvern-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skyvern")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Skyvern is a browser automation platform that uses LLMs and computer vision to interact with websites. The architecture consists of:' in text, "expected to find: " + 'Skyvern is a browser automation platform that uses LLMs and computer vision to interact with websites. The architecture consists of:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Browser Engine** (`skyvern/webeye/`): Playwright-based browser automation with computer vision' in text, "expected to find: " + '- **Browser Engine** (`skyvern/webeye/`): Playwright-based browser automation with computer vision'[:80]

