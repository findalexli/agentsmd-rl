"""Behavioral checks for docs-add-icons-to-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Common Tabler names that differ from FontAwesome: `home` (not `house`), `tool`/`tools` (not `wrench`), `player-play` (not `play`), `bulb` (not `lightbulb`), `alert-triangle` (not `exclamation-triang' in text, "expected to find: " + '- Common Tabler names that differ from FontAwesome: `home` (not `house`), `tool`/`tools` (not `wrench`), `player-play` (not `play`), `bulb` (not `lightbulb`), `alert-triangle` (not `exclamation-triang'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- For providers or brands without a Tabler icon, use a local SVG file in `src/images/providers/` with `currentColor` for theme adaptability (e.g., `icon="/images/providers/anthropic-icon.svg"`)' in text, "expected to find: " + '- For providers or brands without a Tabler icon, use a local SVG file in `src/images/providers/` with `currentColor` for theme adaptability (e.g., `icon="/images/providers/anthropic-icon.svg"`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This project uses the **Tabler** icon library (`"icons": { "library": "tabler" }` in `docs.json`). When adding or updating icons:' in text, "expected to find: " + 'This project uses the **Tabler** icon library (`"icons": { "library": "tabler" }` in `docs.json`). When adding or updating icons:'[:80]

