"""Behavioral checks for backpack-ai-add-agentsmd-to-provide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backpack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Backpack uses design tokens and typography mixins for consistent styling across all components. The token system is built on top of `@skyscanner/bpk-foundations-web` and provides access to all design ' in text, "expected to find: " + 'Backpack uses design tokens and typography mixins for consistent styling across all components. The token system is built on top of `@skyscanner/bpk-foundations-web` and provides access to all design '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Backpack provides a comprehensive set of typography mixins for consistent text styling. Use these instead of setting font properties manually. There are more options available in `unstable__bpk-mixins' in text, "expected to find: " + 'Backpack provides a comprehensive set of typography mixins for consistent text styling. Use these instead of setting font properties manually. There are more options available in `unstable__bpk-mixins'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Backpack** is Skyscanner's design system - a collection of design resources, reusable components, and guidelines for creating consistent user interfaces across Skyscanner's products." in text, "expected to find: " + "**Backpack** is Skyscanner's design system - a collection of design resources, reusable components, and guidelines for creating consistent user interfaces across Skyscanner's products."[:80]

