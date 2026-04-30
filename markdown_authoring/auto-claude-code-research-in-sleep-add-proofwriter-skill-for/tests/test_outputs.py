"""Behavioral checks for auto-claude-code-research-in-sleep-add-proofwriter-skill-for (markdown_authoring task).

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
    text = _read('skills/proof-writer/SKILL.md')
    assert 'description: Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing proof steps, formalize a proof sketch, 补全证明, 写证明' in text, "expected to find: " + 'description: Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing proof steps, formalize a proof sketch, 补全证明, 写证明'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proof-writer/SKILL.md')
    assert "- if the proof uses an equivalent normalization that is stronger in appearance than the user's original theorem statement, label it explicitly as a proof device and keep the original claim separate" in text, "expected to find: " + "- if the proof uses an equivalent normalization that is stronger in appearance than the user's original theorem statement, label it explicitly as a proof device and keep the original claim separate"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proof-writer/SKILL.md')
    assert 'If you use a stronger normalization or cleaner internal formulation only to make the proof easier, keep that as an internal proof device rather than silently replacing the original claim.' in text, "expected to find: " + 'If you use a stronger normalization or cleaner internal formulation only to make the proof easier, keep that as an internal proof device rather than silently replacing the original claim.'[:80]

