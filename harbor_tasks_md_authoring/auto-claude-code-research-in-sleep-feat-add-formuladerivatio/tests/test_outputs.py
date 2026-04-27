"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-formuladerivatio (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/formula-derivation/SKILL.md')
    assert 'description: Structures and derives research formulas when the user wants to 推导公式, build a theory line, organize assumptions, turn scattered equations into a coherent derivation, or rewrite theory not' in text, "expected to find: " + 'description: Structures and derives research formulas when the user wants to 推导公式, build a theory line, organize assumptions, turn scattered equations into a coherent derivation, or rewrite theory not'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/formula-derivation/SKILL.md')
    assert 'If the derivation still lacks a coherent object, stable assumptions, or an honest path from premises to result, downgrade the status and write a blocker report instead of forcing a clean story.' in text, "expected to find: " + 'If the derivation still lacks a coherent object, stable assumptions, or an honest path from premises to result, downgrade the status and write a blocker report instead of forcing a clean story.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/formula-derivation/SKILL.md')
    assert 'If the target, object, notation, or assumptions are ambiguous, state the exact interpretation you are using before deriving anything.' in text, "expected to find: " + 'If the target, object, notation, or assumptions are ambiguous, state the exact interpretation you are using before deriving anything.'[:80]

