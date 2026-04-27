"""Behavioral checks for symfony-ux-skills-fix-design-of-ascii-illustration (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/symfony-ux-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/symfony-ux/SKILL.md')
    assert '|                     Page                            |' in text, "expected to find: " + '|                     Page                            |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/symfony-ux/SKILL.md')
    assert '|  | Turbo Drive (automatic full-page AJAX)         | |' in text, "expected to find: " + '|  | Turbo Drive (automatic full-page AJAX)         | |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/symfony-ux/SKILL.md')
    assert '|  |  | Turbo Frame (partial section)            |  | |' in text, "expected to find: " + '|  |  | Turbo Frame (partial section)            |  | |'[:80]

