"""Behavioral checks for mlflow-document-uv-run-frozen-flag (markdown_authoring task).

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
    assert 'If PyPI is unreachable, add `--frozen` to `uv run` commands that should use the existing `uv.lock` as-is without modifying the environment. This works when the required dependencies are already instal' in text, "expected to find: " + 'If PyPI is unreachable, add `--frozen` to `uv run` commands that should use the existing `uv.lock` as-is without modifying the environment. This works when the required dependencies are already instal'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '### Offline / No-Network Usage' in text, "expected to find: " + '### Offline / No-Network Usage'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'uv run --frozen pytest tests/' in text, "expected to find: " + 'uv run --frozen pytest tests/'[:80]

