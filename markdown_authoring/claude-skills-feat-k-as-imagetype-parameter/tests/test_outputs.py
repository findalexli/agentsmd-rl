"""Behavioral checks for claude-skills-feat-k-as-imagetype-parameter (markdown_authoring task).

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
    assert "**Tradeoffs**: K=64 on the Mona Lisa produces ~2300 shapes (~1.2MB SVG) vs K=32's ~1000 shapes (~550KB). Processing time roughly doubles. The quality gain in tonal gradation is substantial for photos " in text, "expected to find: " + "**Tradeoffs**: K=64 on the Mona Lisa produces ~2300 shapes (~1.2MB SVG) vs K=32's ~1000 shapes (~550KB). Processing time roughly doubles. The quality gain in tonal gradation is substantial for photos "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert '4. **Isolation filter** removes small dark shapes (<500px) that are surrounded by non-dark territory (dark_ratio < 0.3). At higher K, more boundary artifacts appear as isolated dark fragments in light' in text, "expected to find: " + '4. **Isolation filter** removes small dark shapes (<500px) that are surrounded by non-dark territory (dark_ratio < 0.3). At higher K, more boundary artifacts appear as isolated dark fragments in light'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('image-to-svg/SKILL.md')
    assert 'The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Three mechanisms prevent' in text, "expected to find: " + 'The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Three mechanisms prevent'[:80]

