"""Behavioral checks for app-store-screenshots-add-multilanguage-screenshot-support (markdown_authoring task).

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
    assert '10. **Localized screenshots** — "Do you want screenshots in multiple languages? This helps your listing rank in regional App Stores even if your app is English-only. If yes: which languages? (e.g. en,' in text, "expected to find: " + '10. **Localized screenshots** — "Do you want screenshots in multiple languages? This helps your listing rank in regional App Stores even if your app is English-only. If yes: which languages? (e.g. en,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert '**Multi-language:** nest screenshots under a locale folder per language. The generator switches the `base` path; all slide image srcs stay identical.' in text, "expected to find: " + '**Multi-language:** nest screenshots under a locale folder per language. The generator switches the `base` path; all slide image srcs stay identical.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert 'Add a `LOCALES` array and locale tabs to the toolbar. Every slide src uses `base` — no hardcoded paths:' in text, "expected to find: " + 'Add a `LOCALES` array and locale tabs to the toolbar. Every slide src uses `base` — no hardcoded paths:'[:80]

