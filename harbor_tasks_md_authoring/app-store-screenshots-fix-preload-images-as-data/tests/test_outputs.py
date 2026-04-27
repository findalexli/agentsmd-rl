"""Behavioral checks for app-store-screenshots-fix-preload-images-as-data (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/app-store-screenshots")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert '`html-to-image` works by cloning the DOM into an SVG `<foreignObject>`, then painting it to a canvas. During cloning, it re-fetches every `<img>` src. These re-fetches are non-deterministic — some hit' in text, "expected to find: " + '`html-to-image` works by cloning the DOM into an SVG `<foreignObject>`, then painting it to a canvas. During cloning, it re-fetches every `<img>` src. These re-fetches are non-deterministic — some hit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert '- **Pre-loaded data URIs**: Always use the `img()` helper with pre-loaded base64 data URIs for all `<img>` sources. Never use raw file paths in slide components — `html-to-image` will fail to capture ' in text, "expected to find: " + '- **Pre-loaded data URIs**: Always use the `img()` helper with pre-loaded base64 data URIs for all `<img>` sources. Never use raw file paths in slide components — `html-to-image` will fail to capture '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert '**Also flatten RGBA source images to RGB before use.** If your app screenshots are RGBA PNGs, `html-to-image` can fail to serialize them. Convert source images to RGB (no alpha) before placing them in' in text, "expected to find: " + '**Also flatten RGBA source images to RGB before use.** If your app screenshots are RGBA PNGs, `html-to-image` can fail to serialize them. Convert source images to RGB (no alpha) before placing them in'[:80]

