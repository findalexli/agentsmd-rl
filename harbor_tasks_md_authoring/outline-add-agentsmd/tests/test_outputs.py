"""Behavioral checks for outline-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/outline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Outline is a fast, collaborative knowledge base built for teams. It's built with React and TypeScript in both frontend and backend, uses a real-time collaboration engine, and is designed for excellent" in text, "expected to find: " + "Outline is a fast, collaborative knowledge base built for teams. It's built with React and TypeScript in both frontend and backend, uses a real-time collaboration engine, and is designed for excellent"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep API routes thin, use model methods for business logic, or commands if logic spans multiple models.' in text, "expected to find: " + '- Keep API routes thin, use model methods for business logic, or commands if logic spans multiple models.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Avoid unnecessary re-renders by using React.memo, useMemo, and useCallback appropriately.' in text, "expected to find: " + '- Avoid unnecessary re-renders by using React.memo, useMemo, and useCallback appropriately.'[:80]

