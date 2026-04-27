"""Behavioral checks for open-skills-add-citytourismwebsitebuilder-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-tourism-website-builder/SKILL.md')
    assert 'This skill combines research, design, and technical implementation to create professional city tourism websites that showcase the best of any destination.' in text, "expected to find: " + 'This skill combines research, design, and technical implementation to create professional city tourism websites that showcase the best of any destination.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-tourism-website-builder/SKILL.md')
    assert 'description: Research and create modern, animated tourism websites for cities with historical facts, places to visit, and colorful designs.' in text, "expected to find: " + 'description: Research and create modern, animated tourism websites for cities with historical facts, places to visit, and colorful designs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/city-tourism-website-builder/SKILL.md')
    assert 'Create stunning, modern tourism websites for any city with comprehensive research, historical facts, and beautiful animations.' in text, "expected to find: " + 'Create stunning, modern tourism websites for any city with comprehensive research, historical facts, and beautiful animations.'[:80]

