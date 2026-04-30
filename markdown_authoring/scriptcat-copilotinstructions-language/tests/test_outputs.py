"""Behavioral checks for scriptcat-copilotinstructions-language (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scriptcat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The user interface supports multiple languages, with English set as the default for global users.' in text, "expected to find: " + '- The user interface supports multiple languages, with English set as the default for global users.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The code is developed and maintained by developers based in Mainland China.' in text, "expected to find: " + '- The code is developed and maintained by developers based in Mainland China.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Comments should preferably be written in Simplified Chinese.' in text, "expected to find: " + '- Comments should preferably be written in Simplified Chinese.'[:80]

