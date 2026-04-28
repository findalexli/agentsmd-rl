"""Behavioral checks for eris-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eris")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When performing a code review, make sure all properties/methods in classes and objects, where applicable, and including documentation, is listed in alphabetical order. The only exceptions to this are ' in text, "expected to find: " + 'When performing a code review, make sure all properties/methods in classes and objects, where applicable, and including documentation, is listed in alphabetical order. The only exceptions to this are '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When performing a code review, make sure class getters are positioned before class methods.' in text, "expected to find: " + 'When performing a code review, make sure class getters are positioned before class methods.'[:80]

