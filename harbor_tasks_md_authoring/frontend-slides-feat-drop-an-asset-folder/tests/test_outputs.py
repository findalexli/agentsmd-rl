"""Behavioral checks for frontend-slides-feat-drop-an-asset-folder (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/frontend-slides")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Logo in previews (if available):** If the user provided images in Step 1.2 and a logo was identified as `USABLE`, embed it (base64) into each of the 3 style previews. This creates a "wow moment" — t' in text, "expected to find: " + '**Logo in previews (if available):** If the user provided images in Step 1.2 and a logo was identified as `USABLE`, embed it (base64) into each of the 3 style previews. This creates a "wow moment" — t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**User-provided assets are important visual anchors** — but not every asset is necessarily usable. The first step is always to evaluate. After evaluation, the curated assets become additional context ' in text, "expected to find: " + '**User-provided assets are important visual anchors** — but not every asset is necessarily usable. The first step is always to evaluate. After evaluation, the curated assets become additional context '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**If user selected "No images"** → Skip the entire image pipeline. Proceed directly to Phase 2 (Style Discovery) and Phase 3 (Generate Presentation) using text content only. The presentation will use ' in text, "expected to find: " + '**If user selected "No images"** → Skip the entire image pipeline. Proceed directly to Phase 2 (Style Discovery) and Phase 3 (Generate Presentation) using text content only. The presentation will use '[:80]

