"""Behavioral checks for helix-make-claude-read-the-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/helix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file contains critical development guidelines and context that MUST be followed at all times during Helix development.' in text, "expected to find: " + 'This file contains critical development guidelines and context that MUST be followed at all times during Helix development.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This means you often don't need to rebuild containers - just save files and changes are picked up automatically." in text, "expected to find: " + "This means you often don't need to rebuild containers - just save files and changes are picked up automatically."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Naming convention: `YYYY-MM-DD-descriptive-name.md` (e.g., `2025-09-23-wolf-streaming-architecture.md`)' in text, "expected to find: " + '- Naming convention: `YYYY-MM-DD-descriptive-name.md` (e.g., `2025-09-23-wolf-streaming-architecture.md`)'[:80]

