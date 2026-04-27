"""Behavioral checks for claude-skills-fix-boundaryaware-contour-extraction-v130 (markdown_authoring task).

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
    assert '- `edge_density > 0.15`: Keeps shapes with even modest edge alignment. Previous value of 0.3 filtered legitimate dark features like nostrils, lip shadows, brow lines.' in text, "expected to find: " + '- `edge_density > 0.15`: Keeps shapes with even modest edge alignment. Previous value of 0.3 filtered legitimate dark features like nostrils, lip shadows, brow lines.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert '- `compactness > 0.08`: Keeps all but the thinnest ribbon artifacts. Previous value of 0.15 was too aggressive — filtered real facial detail.' in text, "expected to find: " + '- `compactness > 0.08`: Keeps all but the thinnest ribbon artifacts. Previous value of 0.15 was too aggressive — filtered real facial detail.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert 'if not (compactness > 0.08 or edge_density > 0.15' in text, "expected to find: " + 'if not (compactness > 0.08 or edge_density > 0.15'[:80]

