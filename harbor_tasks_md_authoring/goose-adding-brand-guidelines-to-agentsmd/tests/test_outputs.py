"""Behavioral checks for goose-adding-brand-guidelines-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('documentation/AGENTS.md')
    assert '**IMPORTANT**: The product name "goose" should ALWAYS be written in lowercase "g" in all documentation, blog posts, and any content within this documentation directory.' in text, "expected to find: " + '**IMPORTANT**: The product name "goose" should ALWAYS be written in lowercase "g" in all documentation, blog posts, and any content within this documentation directory.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('documentation/AGENTS.md')
    assert 'When editing or creating content in this documentation directory, always ensure "goose" uses a lowercase "g".' in text, "expected to find: " + 'When editing or creating content in this documentation directory, always ensure "goose" uses a lowercase "g".'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('documentation/AGENTS.md')
    assert 'This is a brand guideline that must be strictly followed.' in text, "expected to find: " + 'This is a brand guideline that must be strictly followed.'[:80]

