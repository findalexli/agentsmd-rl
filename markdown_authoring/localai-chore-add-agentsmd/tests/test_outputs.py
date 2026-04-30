"""Behavioral checks for localai-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/localai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Building and testing the project depends on the components involved and the platform where development is taking place. Due to the amount of context required it's usually best not to try building or t" in text, "expected to find: " + "Building and testing the project depends on the components involved and the platform where development is taking place. Due to the amount of context required it's usually best not to try building or t"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use comments sparingly to explain why code does something, not what it does. Comments are there to add context that would be difficult to deduce from reading the code.' in text, "expected to find: " + '- Use comments sparingly to explain why code does something, not what it does. Comments are there to add context that would be difficult to deduce from reading the code.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use `github.com/mudler/xlog` for logging which has the same API as slog.' in text, "expected to find: " + 'Use `github.com/mudler/xlog` for logging which has the same API as slog.'[:80]

