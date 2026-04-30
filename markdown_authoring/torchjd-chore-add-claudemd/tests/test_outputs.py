"""Behavioral checks for torchjd-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/torchjd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Only generate docstrings for public functions or functions that contain more than 4 lines of code.' in text, "expected to find: " + '- Only generate docstrings for public functions or functions that contain more than 4 lines of code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- After generating code, please run `uv run ty check`, `uv run ruff check` and `uv run ruff format`.' in text, "expected to find: " + '- After generating code, please run `uv run ty check`, `uv run ruff check` and `uv run ruff format`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- After changing anything in `src` or in `tests/unit` or `tests/doc`, please identify the affected' in text, "expected to find: " + '- After changing anything in `src` or in `tests/unit` or `tests/doc`, please identify the affected'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

