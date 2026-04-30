"""Behavioral checks for opentrons-chorecursor-update-css-modules-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentrons")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert '- Use snake_case for class names (e.g., `.navbar_link`, `.nav_container`, `.bottom_container`)' in text, "expected to find: " + '- Use snake_case for class names (e.g., `.navbar_link`, `.nav_container`, `.bottom_container`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert '- `color` and `background-color` (e.g., `var(--white)`, `var(--black-90)`, `var(--blue-50)`)' in text, "expected to find: " + '- `color` and `background-color` (e.g., `var(--white)`, `var(--black-90)`, `var(--blue-50)`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert 'description: Ensures CSS Modules file follows stylelint and Opentrons CSS conventions' in text, "expected to find: " + 'description: Ensures CSS Modules file follows stylelint and Opentrons CSS conventions'[:80]

