"""Behavioral checks for antigravity-awesome-skills-feat-add-progressiveestimation-sk (markdown_authoring task).

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
    text = _read('skills/progressive-estimation/SKILL.md')
    assert "Progressive Estimation adapts to your team's working mode — human-only, hybrid, or agent-first — applying the right velocity model and multipliers for each. It produces statistical estimates rather th" in text, "expected to find: " + "Progressive Estimation adapts to your team's working mode — human-only, hybrid, or agent-first — applying the right velocity model and multipliers for each. It produces statistical estimates rather th"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/progressive-estimation/SKILL.md')
    assert 'Estimate AI-assisted and hybrid human+agent development work using research-backed formulas with PERT statistics, confidence bands, and calibration feedback loops.' in text, "expected to find: " + 'Estimate AI-assisted and hybrid human+agent development work using research-backed formulas with PERT statistics, confidence bands, and calibration feedback loops.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/progressive-estimation/SKILL.md')
    assert 'description: "Estimate AI-assisted and hybrid human+agent development work with research-backed PERT statistics and calibration feedback loops"' in text, "expected to find: " + 'description: "Estimate AI-assisted and hybrid human+agent development work with research-backed PERT statistics and calibration feedback loops"'[:80]

