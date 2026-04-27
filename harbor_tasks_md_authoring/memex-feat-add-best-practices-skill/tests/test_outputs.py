"""Behavioral checks for memex-feat-add-best-practices-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/memex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/memex-best-practices/SKILL.md')
    assert "This loop is implemented by the `memex-recall` and `memex-retro` skills. The key insight: **retro is not just documentation — it's how you learn**. Writing in your own words forces deeper understandin" in text, "expected to find: " + "This loop is implemented by the `memex-recall` and `memex-retro` skills. The key insight: **retro is not just documentation — it's how you learn**. Writing in your own words forces deeper understandin"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/memex-best-practices/SKILL.md')
    assert 'description: Zettelkasten best practices for building a high-quality, long-lived knowledge graph with memex. Reference guide for card writing, naming, tagging, linking, and graph maintenance.' in text, "expected to find: " + 'description: Zettelkasten best practices for building a high-quality, long-lived knowledge graph with memex. Reference guide for card writing, naming, tagging, linking, and graph maintenance.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/memex-best-practices/SKILL.md')
    assert "When two cards disagree, this is valuable signal — not a bug. The organize skill flags contradictions with `status: conflict` for human resolution. Don't auto-resolve conflicting beliefs." in text, "expected to find: " + "When two cards disagree, this is valuable signal — not a bug. The organize skill flags contradictions with `status: conflict` for human resolution. Don't auto-resolve conflicting beliefs."[:80]

