"""Behavioral checks for app-store-screenshots-feat-add-ipad-app-store (markdown_authoring task).

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
    assert 'When supporting both devices, add a toggle (iPhone / iPad) in the toolbar next to the size dropdown. The size dropdown should switch between iPhone and iPad sizes based on the selected device. Support' in text, "expected to find: " + 'When supporting both devices, add a toggle (iPhone / iPad) in the toolbar next to the size dropdown. The size dropdown should switch between iPhone and iPad sizes based on the selected device. Support'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert "The skill includes a pre-measured iPhone mockup at `mockup.png` (co-located with this SKILL.md). Copy it to the project's `public/` directory. The mockup file is in the same directory as this skill fi" in text, "expected to find: " + "The skill includes a pre-measured iPhone mockup at `mockup.png` (co-located with this SKILL.md). Copy it to the project's `public/` directory. The mockup file is in the same directory as this skill fi"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/app-store-screenshots/SKILL.md')
    assert '**Critical dimension:** The frame aspect ratio must be `770/1000` so the inner screen area (92% width × 94.4% height) matches the 3:4 aspect ratio of iPad screenshots. Using incorrect proportions caus' in text, "expected to find: " + '**Critical dimension:** The frame aspect ratio must be `770/1000` so the inner screen area (92% width × 94.4% height) matches the 3:4 aspect ratio of iPad screenshots. Using incorrect proportions caus'[:80]

