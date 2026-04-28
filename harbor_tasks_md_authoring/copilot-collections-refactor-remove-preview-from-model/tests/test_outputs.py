"""Behavioral checks for copilot-collections-refactor-remove-preview-from-model (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-collections")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/implement-ui.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/implement.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/plan.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/research.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/review-ui.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/review.prompt.md')
    assert 'model: "Claude Opus 4.5"' in text, "expected to find: " + 'model: "Claude Opus 4.5"'[:80]

