"""Behavioral checks for mlflow-add-clint-custom-linter-command (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mlflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'uv run clint .                    # Run MLflow custom linter' in text, "expected to find: " + 'uv run clint .                    # Run MLflow custom linter'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Custom MLflow linting with Clint' in text, "expected to find: " + '# Custom MLflow linting with Clint'[:80]

