"""Behavioral checks for nanostack-add-visual-qa-for-uiux (markdown_authoring task).

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
    text = _read('qa/SKILL.md')
    assert 'After functional tests pass, take screenshots of every key state and analyze the UI visually. This is not optional for web apps. A feature that works but looks broken is broken.' in text, "expected to find: " + 'After functional tests pass, take screenshots of every key state and analyze the UI visually. This is not optional for web apps. A feature that works but looks broken is broken.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**Cross-reference against `/nano-plan` product standards.** If the plan said "shadcn/ui + Tailwind" and the output looks like raw HTML with inline styles, that\'s a finding.' in text, "expected to find: " + '**Cross-reference against `/nano-plan` product standards.** If the plan said "shadcn/ui + Tailwind" and the output looks like raw HTML with inline styles, that\'s a finding.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert 'Visual findings are should_fix by default. Blocking only if the UI is unusable (overlapping elements, invisible text, broken layout at common viewport sizes).' in text, "expected to find: " + 'Visual findings are should_fix by default. Blocking only if the UI is unusable (overlapping elements, invisible text, broken layout at common viewport sizes).'[:80]

