"""Behavioral checks for antigravity-awesome-skills-update-skillmd-to-final-version (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyze-project/SKILL.md')
    assert 'Analyze AI-assisted coding sessions in `~/.gemini/antigravity/brain/` and produce a report that explains not just **what happened**, but **why it happened**, **who/what caused it**, and **what should ' in text, "expected to find: " + 'Analyze AI-assisted coding sessions in `~/.gemini/antigravity/brain/` and produce a report that explains not just **what happened**, but **why it happened**, **who/what caused it**, and **what should '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyze-project/SKILL.md')
    assert 'Then add a short narrative summary of what is going well, what is breaking down, and whether the main issue is prompt quality, repo fragility, workflow discipline, or validation churn.' in text, "expected to find: " + 'Then add a short narrative summary of what is going well, what is breaking down, and whether the main issue is prompt quality, repo fragility, workflow discipline, or validation churn.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyze-project/SKILL.md')
    assert 'Show the files/folders/subsystems most associated with replanning, abandonment, verification churn, and high severity.' in text, "expected to find: " + 'Show the files/folders/subsystems most associated with replanning, abandonment, verification churn, and high severity.'[:80]

