"""Behavioral checks for gemini-cli-desktop-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gemini-cli-desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '*This documentation is maintained alongside the codebase and should be updated when significant changes are made to the architecture, APIs, or development processes.*' in text, "expected to find: " + '*This documentation is maintained alongside the codebase and should be updated when significant changes are made to the architecture, APIs, or development processes.*'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The application uses a sophisticated proxy-based API system that automatically routes calls to either Tauri commands (desktop) or REST endpoints (web):' in text, "expected to find: " + 'The application uses a sophisticated proxy-based API system that automatically routes calls to either Tauri commands (desktop) or REST endpoints (web):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **File viewing support**: PDF, Excel, image, and text file viewers with syntax highlighting' in text, "expected to find: " + '- **File viewing support**: PDF, Excel, image, and text file viewers with syntax highlighting'[:80]

