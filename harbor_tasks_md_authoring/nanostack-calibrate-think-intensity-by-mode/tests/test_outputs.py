"""Behavioral checks for nanostack-calibrate-think-intensity-by-mode (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '**How to detect the mode:** If the user describes a personal pain ("I have this problem," "I need to..."), default to Startup or Builder. If the user pitches an idea for others ("I want to build X for' in text, "expected to find: " + '**How to detect the mode:** If the user describes a personal pain ("I have this problem," "I need to..."), default to Startup or Builder. If the user pitches an idea for others ("I want to build X for'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '- **Founder mode**: Experienced entrepreneur stress-testing an idea. Wants to be challenged hard. Applies full YC diagnostic with maximum pushback. Use when the user explicitly asks for a tough review' in text, "expected to find: " + '- **Founder mode**: Experienced entrepreneur stress-testing an idea. Wants to be challenged hard. Applies full YC diagnostic with maximum pushback. Use when the user explicitly asks for a tough review'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '- **Startup mode** (default for product ideas): Building a product for users/customers. Applies YC diagnostic. Challenges scope and approach but respects stated pain points.' in text, "expected to find: " + '- **Startup mode** (default for product ideas): Building a product for users/customers. Applies YC diagnostic. Challenges scope and approach but respects stated pain points.'[:80]

