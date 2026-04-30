"""Behavioral checks for hex1b-add-writingunittests-and-apireviewer-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hex1b")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/api-reviewer/SKILL.md')
    assert 'This skill captures API design preferences for the Hex1b codebase. Use it when reviewing public APIs, evaluating whether code should be public or internal, or assessing API design decisions made by AI' in text, "expected to find: " + 'This skill captures API design preferences for the Hex1b codebase. Use it when reviewing public APIs, evaluating whether code should be public or internal, or assessing API design decisions made by AI'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/api-reviewer/SKILL.md')
    assert 'description: Guidelines for reviewing API design in the Hex1b codebase. Use when evaluating public APIs, reviewing accessibility modifiers, or assessing whether new APIs follow project conventions.' in text, "expected to find: " + 'description: Guidelines for reviewing API design in the Hex1b codebase. Use when evaluating public APIs, reviewing accessibility modifiers, or assessing whether new APIs follow project conventions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/api-reviewer/SKILL.md')
    assert '**Design note**: Hex1bTerminal emerged from the need to properly test TUI components. The adapter pattern enables use in real terminals, unit tests, or projecting state across networks.' in text, "expected to find: " + '**Design note**: Hex1bTerminal emerged from the need to properly test TUI components. The adapter pattern enables use in real terminals, unit tests, or projecting state across networks.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/writing-unit-tests/SKILL.md')
    assert '**Problem**: Rendering is inherently async. Finding "Header" doesn\'t guarantee "Footer" has rendered yet. This is especially problematic when testing other terminal frameworks (like Spectre Console) w' in text, "expected to find: " + '**Problem**: Rendering is inherently async. Finding "Header" doesn\'t guarantee "Footer" has rendered yet. This is especially problematic when testing other terminal frameworks (like Spectre Console) w'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/writing-unit-tests/SKILL.md')
    assert "**Guideline**: If you're going to assert on specific screen content, include it in the `WaitUntil` condition. Don't assume the rest of the screen is ready just because one part appeared." in text, "expected to find: " + "**Guideline**: If you're going to assert on specific screen content, include it in the `WaitUntil` condition. Don't assume the rest of the screen is ready just because one part appeared."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/writing-unit-tests/SKILL.md')
    assert 'This skill provides guidelines for AI agents writing unit tests for the Hex1b TUI library. It outlines the preferred testing approach, patterns, and anti-patterns to avoid.' in text, "expected to find: " + 'This skill provides guidelines for AI agents writing unit tests for the Hex1b TUI library. It outlines the preferred testing approach, patterns, and anti-patterns to avoid.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository includes specialized skills in `.github/skills/` that provide detailed guidance for specific tasks. **Invoke these skills when working on related tasks** - they contain step-by-step pr' in text, "expected to find: " + 'This repository includes specialized skills in `.github/skills/` that provide detailed guidance for specific tasks. **Invoke these skills when working on related tasks** - they contain step-by-step pr'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Skills are invoked automatically by AI agents based on the task context. They contain comprehensive procedures that complement the high-level guidance in this file.' in text, "expected to find: " + 'Skills are invoked automatically by AI agents based on the task context. They contain comprehensive procedures that complement the high-level guidance in this file.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **📘 Use the `widget-creator` skill** for comprehensive step-by-step guidance including templates, theming, and test patterns.' in text, "expected to find: " + '> **📘 Use the `widget-creator` skill** for comprehensive step-by-step guidance including templates, theming, and test patterns.'[:80]

