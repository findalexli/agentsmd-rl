"""Behavioral checks for marvin-delete-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marvin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/docs.mdc')
    assert '.cursor/rules/docs.mdc' in text, "expected to find: " + '.cursor/rules/docs.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert '.cursor/rules/general.mdc' in text, "expected to find: " + '.cursor/rules/general.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python.mdc')
    assert '.cursor/rules/python.mdc' in text, "expected to find: " + '.cursor/rules/python.mdc'[:80]

