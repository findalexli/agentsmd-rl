"""Behavioral checks for claude-skills-featengineering-add-demovideo-skill (markdown_authoring task).

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
    text = _read('engineering/demo-video/SKILL.md')
    assert 'description: "Use when the user asks to create a demo video, product walkthrough, feature showcase, animated presentation, marketing video, or GIF from screenshots or scene descriptions. Orchestrates ' in text, "expected to find: " + 'description: "Use when the user asks to create a demo video, product walkthrough, feature showcase, animated presentation, marketing video, or GIF from screenshots or scene descriptions. Orchestrates '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/demo-video/SKILL.md')
    assert 'Create polished demo videos by orchestrating browser rendering, text-to-speech, and video compositing. Think like a video producer — story arc, pacing, emotion, visual hierarchy. Turns screenshots and' in text, "expected to find: " + 'Create polished demo videos by orchestrating browser rendering, text-to-speech, and video compositing. Think like a video producer — story arc, pacing, emotion, visual hierarchy. Turns screenshots and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/demo-video/SKILL.md')
    assert 'Background: dark with subtle purple-blue glow gradients. Screenshots: always `border-radius: 12px` with `box-shadow`. Easing: always `cubic-bezier(0.16, 1, 0.3, 1)` — never `ease` or `linear`.' in text, "expected to find: " + 'Background: dark with subtle purple-blue glow gradients. Screenshots: always `border-radius: 12px` with `box-shadow`. Easing: always `cubic-bezier(0.16, 1, 0.3, 1)` — never `ease` or `linear`.'[:80]

