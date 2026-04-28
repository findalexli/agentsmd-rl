"""Behavioral checks for tiny-llm-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tiny-llm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `pdm run test --week X --day Y` auto-copies `tests_refsol/test_week_X_day_Y.py` into `tests/`.' in text, "expected to find: " + '- `pdm run test --week X --day Y` auto-copies `tests_refsol/test_week_X_day_Y.py` into `tests/`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Model-dependent tests (0.5B/1.5B/7B) skip when models are not downloaded locally.' in text, "expected to find: " + '- Model-dependent tests (0.5B/1.5B/7B) skip when models are not downloaded locally.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run and verify tests in a way that matches the book workflow (`book/src/*.md`).' in text, "expected to find: " + '- Run and verify tests in a way that matches the book workflow (`book/src/*.md`).'[:80]

