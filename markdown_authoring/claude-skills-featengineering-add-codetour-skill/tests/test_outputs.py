"""Behavioral checks for claude-skills-featengineering-add-codetour-skill (markdown_authoring task).

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
    text = _read('engineering/code-tour/SKILL.md')
    assert 'description: "Use when the user asks to create a CodeTour .tour file — persona-targeted, step-by-step walkthroughs that link to real files and line numbers. Trigger for: create a tour, onboarding tour' in text, "expected to find: " + 'description: "Use when the user asks to create a CodeTour .tour file — persona-targeted, step-by-step walkthroughs that link to real files and line numbers. Trigger for: create a tour, onboarding tour'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/code-tour/SKILL.md')
    assert 'Create **CodeTour** files — persona-targeted, step-by-step walkthroughs of a codebase that link directly to files and line numbers. CodeTour files live in `.tours/` and work with the [VS Code CodeTour' in text, "expected to find: " + 'Create **CodeTour** files — persona-targeted, step-by-step walkthroughs of a codebase that link directly to files and line numbers. CodeTour files live in `.tours/` and work with the [VS Code CodeTour'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/code-tour/SKILL.md')
    assert 'A great tour is a **narrative** — a story told to a specific person about what matters, why it matters, and what to do next. Only create `.tour` JSON files. Never modify source code.' in text, "expected to find: " + 'A great tour is a **narrative** — a story told to a specific person about what matters, why it matters, and what to do next. Only create `.tour` JSON files. Never modify source code.'[:80]

