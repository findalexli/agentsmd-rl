"""Behavioral checks for claude-skills-fix-boundaryaware-contour-extraction-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert "**Why this works**: Boundary artifacts are thin (low compactness) AND don't correspond to real structural edges. Real dark features (eyes, hair, outlines in graphic art) have compact shapes or align w" in text, "expected to find: " + "**Why this works**: Boundary artifacts are thin (low compactness) AND don't correspond to real structural edges. Real dark features (eyes, hair, outlines in graphic art) have compact shapes or align w"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert 'The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Two mechanisms prevent t' in text, "expected to find: " + 'The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Two mechanisms prevent t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert 'Use the seeing-images skill to create a reference edge map. This distinguishes real structural boundaries from gradient-transition artifacts during contour extraction.' in text, "expected to find: " + 'Use the seeing-images skill to create a reference edge map. This distinguishes real structural boundaries from gradient-transition artifacts during contour extraction.'[:80]

