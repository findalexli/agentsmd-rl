"""Behavioral checks for cursor-memory-bank-fix-wrong-filename-when-referring (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursor-memory-bank")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc')
    assert 'AssessLevel -->|"Level 4"| L4Archive["LEVEL 4 ARCHIVING<br>Level4/archive-comprehensive.mdc"]' in text, "expected to find: " + 'AssessLevel -->|"Level 4"| L4Archive["LEVEL 4 ARCHIVING<br>Level4/archive-comprehensive.mdc"]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc')
    assert 'AssessLevel -->|"Level 3"| L3Archive["LEVEL 3 ARCHIVING<br>Level3/archive-intermediate.mdc"]' in text, "expected to find: " + 'AssessLevel -->|"Level 3"| L3Archive["LEVEL 3 ARCHIVING<br>Level3/archive-intermediate.mdc"]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc')
    assert 'AssessLevel -->|"Level 2"| L2Archive["LEVEL 2 ARCHIVING<br>Level2/archive-basic.mdc"]' in text, "expected to find: " + 'AssessLevel -->|"Level 2"| L2Archive["LEVEL 2 ARCHIVING<br>Level2/archive-basic.mdc"]'[:80]

