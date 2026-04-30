"""Behavioral checks for detox-cursor-rules-01 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/detox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-idomatic.mdc')
    assert '- Minimize comments usage, especially in-line ones. Leave comments where things are exceptionally unclear for some reason.' in text, "expected to find: " + '- Minimize comments usage, especially in-line ones. Leave comments where things are exceptionally unclear for some reason.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-idomatic.mdc')
    assert '- Whenever an Error needs to be thrown, prefer throwing a DetoxRuntimeError with a proper message and hint.' in text, "expected to find: " + '- Whenever an Error needs to be thrown, prefer throwing a DetoxRuntimeError with a proper message and hint.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-idomatic.mdc')
    assert 'description: Rules to help Cursor write code that is more Detox idomatic' in text, "expected to find: " + 'description: Rules to help Cursor write code that is more Detox idomatic'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-unittests.mdc')
    assert 'Note: `jest.mock()` must still be called at the module level (for hoisting), but all mock configuration should happen in `beforeEach()`.' in text, "expected to find: " + 'Note: `jest.mock()` must still be called at the module level (for hoisting), but all mock configuration should happen in `beforeEach()`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-unittests.mdc')
    assert 'In Jest unit test files, **never perform mocking globally**. Instead, perform all mocks inside the `beforeEach()` section.' in text, "expected to find: " + 'In Jest unit test files, **never perform mocking globally**. Instead, perform all mocks inside the `beforeEach()` section.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/detox-unittests.mdc')
    assert "Alternatively, in cases where jest.mock() doesn't work well out of the box, this can be performed too:" in text, "expected to find: " + "Alternatively, in cases where jest.mock() doesn't work well out of the box, this can be performed too:"[:80]

