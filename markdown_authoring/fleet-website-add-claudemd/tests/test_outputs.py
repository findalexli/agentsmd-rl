"""Behavioral checks for fleet-website-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fleet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert 'Avoid using Bootstrap utility classes (`.d-flex`, `.justify-content-center`, `.flex-column`, etc.) for layout and display properties. Define these styles in the LESS stylesheet using `[purpose]` selec' in text, "expected to find: " + 'Avoid using Bootstrap utility classes (`.d-flex`, `.justify-content-center`, `.flex-column`, etc.) for layout and display properties. Define these styles in the LESS stylesheet using `[purpose]` selec'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert 'Some pages use a `-page` suffix (e.g., `#software-management-page` instead of `#software-management`). This is done when the base name would collide with an auto-generated heading ID — for example, ma' in text, "expected to find: " + 'Some pages use a `-page` suffix (e.g., `#software-management-page` instead of `#software-management`). This is done when the base name would collide with an auto-generated heading ID — for example, ma'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert '- `<parallax-city>` — animated city skyline banner, used at the bottom of landing pages. Must sit at the top level of the page, outside `page-container`/`page-content`, so it can span the full viewpor' in text, "expected to find: " + '- `<parallax-city>` — animated city skyline banner, used at the bottom of landing pages. Must sit at the top level of the page, outside `page-container`/`page-content`, so it can span the full viewpor'[:80]

