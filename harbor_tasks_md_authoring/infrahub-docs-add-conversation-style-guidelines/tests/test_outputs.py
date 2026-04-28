"""Behavioral checks for infrahub-docs-add-conversation-style-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/infrahub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Responses must be direct and substantive. Do not use filler phrases, compliments, or social pleasantries.' in text, "expected to find: " + 'Responses must be direct and substantive. Do not use filler phrases, compliments, or social pleasantries.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- "You\'re right", "You\'re absolutely right", "Great question", "Good idea"' in text, "expected to find: " + '- "You\'re right", "You\'re absolutely right", "Great question", "Good idea"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Frontend:** TypeScript 5.9, React 19.2, Vite 7.3, Tailwind CSS 4.1' in text, "expected to find: " + '- **Frontend:** TypeScript 5.9, React 19.2, Vite 7.3, Tailwind CSS 4.1'[:80]

