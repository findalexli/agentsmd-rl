"""Behavioral checks for mlflow-fix-yarn-command-format-in (markdown_authoring task).

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
    assert '(cd mlflow/server/js && yarn prettier:check)' in text, "expected to find: " + '(cd mlflow/server/js && yarn prettier:check)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '(cd mlflow/server/js && yarn prettier:fix)' in text, "expected to find: " + '(cd mlflow/server/js && yarn prettier:fix)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '(cd mlflow/server/js && yarn type-check)' in text, "expected to find: " + '(cd mlflow/server/js && yarn type-check)'[:80]

