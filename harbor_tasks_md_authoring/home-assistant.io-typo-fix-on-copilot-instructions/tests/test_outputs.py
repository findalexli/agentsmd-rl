"""Behavioral checks for home-assistant.io-typo-fix-on-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/home-assistant.io")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Write from a second-person perspective, using "you" and "your" instead of "the user" or "users".' in text, "expected to find: " + 'Write from a second-person perspective, using "you" and "your" instead of "the user" or "users".'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Write towards the reader directly, and not a group of users.' in text, "expected to find: " + 'Write towards the reader directly, and not a group of users.'[:80]

