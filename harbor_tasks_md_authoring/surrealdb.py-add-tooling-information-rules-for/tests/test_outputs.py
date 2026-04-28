"""Behavioral checks for surrealdb.py-add-tooling-information-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/surrealdb.py")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/tooling.mdc')
    assert 'This project uses `uv` for dependency management and includes several tools for code quality and testing. These should always pass before a tasks is considered complete.' in text, "expected to find: " + 'This project uses `uv` for dependency management and includes several tools for code quality and testing. These should always pass before a tasks is considered complete.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/tooling.mdc')
    assert 'Coverage reports are generated automatically when running tests. View the HTML report:' in text, "expected to find: " + 'Coverage reports are generated automatically when running tests. View the HTML report:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/tooling.mdc')
    assert 'uv run pytest --cov=src/surrealdb --cov-report=term-missing --cov-report=html' in text, "expected to find: " + 'uv run pytest --cov=src/surrealdb --cov-report=term-missing --cov-report=html'[:80]

