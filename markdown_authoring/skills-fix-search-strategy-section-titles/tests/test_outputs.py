"""Behavioral checks for skills-fix-search-strategy-section-titles (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert "Use when: you have a retrieval pipeline in place but results aren't getting better across search iterations." in text, "expected to find: " + "Use when: you have a retrieval pipeline in place but results aren't getting better across search iterations."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert "Use when: you can provide positive and negative example points but don't have a feedback model." in text, "expected to find: " + "Use when: you can provide positive and negative example points but don't have a feedback model."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert "## Know What Good Results Look Like But Can't Get Them" in text, "expected to find: " + "## Know What Good Results Look Like But Can't Get Them"[:80]

