"""Behavioral checks for awesome-copilot-add-author-credits-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-copilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gsap-framer-scroll-animation/SKILL.md')
    assert "author_url: 'https://github.com/utkarsh232005'" in text, "expected to find: " + "author_url: 'https://github.com/utkarsh232005'"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gsap-framer-scroll-animation/SKILL.md')
    assert "author: 'Utkarsh Patrikar'" in text, "expected to find: " + "author: 'Utkarsh Patrikar'"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/premium-frontend-ui/SKILL.md')
    assert "author_url: 'https://github.com/utkarsh232005'" in text, "expected to find: " + "author_url: 'https://github.com/utkarsh232005'"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/premium-frontend-ui/SKILL.md')
    assert "author: 'Utkarsh Patrikar'" in text, "expected to find: " + "author: 'Utkarsh Patrikar'"[:80]

