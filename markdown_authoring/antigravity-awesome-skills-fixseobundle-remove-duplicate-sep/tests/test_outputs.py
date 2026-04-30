"""Behavioral checks for antigravity-awesome-skills-fixseobundle-remove-duplicate-sep (markdown_authoring task).

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
    text = _read('skills/schema-markup/SKILL.md')
    assert 'skills/schema-markup/SKILL.md' in text, "expected to find: " + 'skills/schema-markup/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-fundamentals/SKILL.md')
    assert 'skills/seo-fundamentals/SKILL.md' in text, "expected to find: " + 'skills/seo-fundamentals/SKILL.md'[:80]

