"""Behavioral checks for mediocre-hass-media-player-cards-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mediocre-hass-media-player-cards")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**mediocre-hass-media-player-cards** — Custom Home Assistant Lovelace cards for media player entities. Provides four card types: Standard, Massive, Multi, and Chip Group. Built with Preact + TypeScrip' in text, "expected to find: " + '**mediocre-hass-media-player-cards** — Custom Home Assistant Lovelace cards for media player entities. Provides four card types: Standard, Massive, Multi, and Chip Group. Built with Preact + TypeScrip'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Web Component Wrappers**: Cards extend `CardWrapper` which bridges Lovelace lifecycle to Preact rendering' in text, "expected to find: " + '- **Web Component Wrappers**: Cards extend `CardWrapper` which bridges Lovelace lifecycle to Preact rendering'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Context Providers**: `CardContext`, `PlayerContext`, `HassContext` — shared state via Preact context' in text, "expected to find: " + '- **Context Providers**: `CardContext`, `PlayerContext`, `HassContext` — shared state via Preact context'[:80]

