"""Behavioral checks for claude-skills-add-imagetosvg-skill-v100 (markdown_authoring task).

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
    assert 'description: Convert raster images (photos, paintings, illustrations) into SVG vector reproductions. Use when the user uploads an image and asks to reproduce, vectorize, trace, or convert it to SVG. A' in text, "expected to find: " + 'description: Convert raster images (photos, paintings, illustrations) into SVG vector reproductions. Use when the user uploads an image and asks to reproduce, vectorize, trace, or convert it to SVG. A'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert "**Trust the data, not your imagination.** Claude's visual interpretation of images is unreliable for precise color matching, shape positioning, and spatial relationships. Every shape, color, and posit" in text, "expected to find: " + "**Trust the data, not your imagination.** Claude's visual interpretation of images is unreliable for precise color matching, shape positioning, and spatial relationships. Every shape, color, and posit"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert '**Be conservative with background merging.** Only merge colors that are nearly identical to background AND heavily touch edges. Subtle features (like a gray band between two shapes) will be destroyed ' in text, "expected to find: " + '**Be conservative with background merging.** Only merge colors that are nearly identical to background AND heavily touch edges. Subtle features (like a gray band between two shapes) will be destroyed '[:80]

