"""Behavioral checks for antigravity-awesome-skills-add-productmanager-skill (markdown_authoring task).

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
    text = _read('skills/product-manager/SKILL.md')
    assert 'You are a Senior Product Manager agent with deep expertise across 6 knowledge domains. You apply 30+ proven PM frameworks, use 12 ready-made templates, and calculate 32 SaaS metrics with exact formula' in text, "expected to find: " + 'You are a Senior Product Manager agent with deep expertise across 6 knowledge domains. You apply 30+ proven PM frameworks, use 12 ready-made templates, and calculate 32 SaaS metrics with exact formula'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/product-manager/SKILL.md')
    assert 'Apply frameworks including RICE scoring, MoSCoW prioritization, Jobs-to-be-Done, Kano Model, Opportunity Solution Trees, North Star Metric, Impact Mapping, Story Mapping, and 20+ more.' in text, "expected to find: " + 'Apply frameworks including RICE scoring, MoSCoW prioritization, Jobs-to-be-Done, Kano Model, Opportunity Solution Trees, North Star Metric, Impact Mapping, Story Mapping, and 20+ more.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/product-manager/SKILL.md')
    assert 'Calculate 32 SaaS metrics with exact formulas: MRR, ARR, Churn Rate, LTV, CAC, LTV:CAC Ratio, Net Revenue Retention, Quick Ratio, Rule of 40, Magic Number, and more.' in text, "expected to find: " + 'Calculate 32 SaaS metrics with exact formulas: MRR, ARR, Churn Rate, LTV, CAC, LTV:CAC Ratio, Net Revenue Retention, Quick Ratio, Rule of 40, Magic Number, and more.'[:80]

