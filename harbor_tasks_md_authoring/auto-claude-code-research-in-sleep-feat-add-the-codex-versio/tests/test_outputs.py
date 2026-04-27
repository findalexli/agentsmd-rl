"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-the-codex-versio (markdown_authoring task).

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
    text = _read('skills/skills-codex/formula-derivation/SKILL.md')
    assert 'description: "Structure and derive research formulas when the user wants to 推导公式, derive a theory line, build equations from a problem statement, clarify assumptions, separate formal derivation from r' in text, "expected to find: " + 'description: "Structure and derive research formulas when the user wants to 推导公式, derive a theory line, build equations from a problem statement, clarify assumptions, separate formal derivation from r'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills-codex/formula-derivation/SKILL.md')
    assert 'The derivation must be built around **one invariant object**. Do not start from scattered formulas. Start from the object that survives across regimes, then derive proxies, decompositions, and interpr' in text, "expected to find: " + 'The derivation must be built around **one invariant object**. Do not start from scattered formulas. Start from the object that survives across regimes, then derive proxies, decompositions, and interpr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills-codex/formula-derivation/SKILL.md')
    assert 'Do **not** use this skill as a replacement for strict proof writing once the exact claim is already fixed and the user wants a theorem-proof package. In that case, hand off to `proof-writer`.' in text, "expected to find: " + 'Do **not** use this skill as a replacement for strict proof writing once the exact claim is already fixed and the user wants a theorem-proof package. In that case, hand off to `proof-writer`.'[:80]

