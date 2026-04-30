"""Behavioral checks for sqlframe-docs-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sqlframe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "All PySpark functions live in `sqlframe/base/functions.py` with `@func_metadata` decorator. Each engine's `functions.py` filters to only supported functions by checking `unsupported_engines`. Use `uns" in text, "expected to find: " + "All PySpark functions live in `sqlframe/base/functions.py` with `@func_metadata` decorator. Each engine's `functions.py` filters to only supported functions by checking `unsupported_engines`. Use `uns"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'DataFrame methods are decorated with `@operation(Operation.X)` to track operation order. When incompatible operations are chained, the current expression is wrapped into a CTE before continuing. SQL i' in text, "expected to find: " + 'DataFrame methods are decorated with `@operation(Operation.X)` to track operation order. When incompatible operations are chained, the current expression is wrapped into a CTE before continuing. SQL i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Each engine directory (`sqlframe/duckdb/`, etc.) contains thin subclasses of the base classes. The session's `Builder` sets `DEFAULT_EXECUTION_DIALECT`. Three dialects exist per session: `input_dialec" in text, "expected to find: " + "Each engine directory (`sqlframe/duckdb/`, etc.) contains thin subclasses of the base classes. The session's `Builder` sets `DEFAULT_EXECUTION_DIALECT`. Three dialects exist per session: `input_dialec"[:80]

