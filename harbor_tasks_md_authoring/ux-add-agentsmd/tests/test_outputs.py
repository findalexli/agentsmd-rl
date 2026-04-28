"""Behavioral checks for ux-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ux")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. Ensure to have written tests for any new features or bug fixes, and that all tests pass locally, if it makes sense to do so (e.g. for a pure JS change, running PHP tests is not required).' in text, "expected to find: " + '1. Ensure to have written tests for any new features or bug fixes, and that all tests pass locally, if it makes sense to do so (e.g. for a pure JS change, running PHP tests is not required).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Doc comments**: use `@author` on classes. PHPDoc only when types can't express the contract (generics, union details). Don't duplicate type info already in signatures." in text, "expected to find: " + "- **Doc comments**: use `@author` on classes. PHPDoc only when types can't express the contract (generics, union details). Don't duplicate type info already in signatures."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Stimulus controllers**: extend `Controller` from `@hotwired/stimulus`, use `static values = {}` pattern, `declare readonly` for value properties' in text, "expected to find: " + '- **Stimulus controllers**: extend `Controller` from `@hotwired/stimulus`, use `static values = {}` pattern, `declare readonly` for value properties'[:80]

