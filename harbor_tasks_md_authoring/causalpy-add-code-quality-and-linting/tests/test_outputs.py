"""Behavioral checks for causalpy-add-code-quality-and-linting (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/causalpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Before committing**: Always run `pre-commit run --all-files` to ensure all checks pass (linting, formatting, type checking)' in text, "expected to find: " + '- **Before committing**: Always run `pre-commit run --all-files` to ensure all checks pass (linting, formatting, type checking)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Linting rules**: Project uses strict linting (F, B, UP, C4, SIM, I) to catch bugs and enforce modern Python patterns' in text, "expected to find: " + '- **Linting rules**: Project uses strict linting (F, B, UP, C4, SIM, I) to catch bugs and enforce modern Python patterns'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Quick check**: Run `ruff check causalpy/` for fast linting feedback during development' in text, "expected to find: " + '- **Quick check**: Run `ruff check causalpy/` for fast linting feedback during development'[:80]

