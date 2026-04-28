"""Behavioral checks for recce-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/recce")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **In-Memory State with Persistence**: `RecceContext` holds runtime state (runs, checks, adapter). `CheckDAO` and `RunDAO` provide in-memory storage. `RecceStateLoader` abstraction supports `FileStat' in text, "expected to find: " + '- **In-Memory State with Persistence**: `RecceContext` holds runtime state (runs, checks, adapter). `CheckDAO` and `RunDAO` provide in-memory storage. `RecceStateLoader` abstraction supports `FileStat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Recce is a data validation and review tool for dbt projects. It helps data teams preview, validate, and ship data changes with confidence by providing lineage visualization, data diffing, and collabor' in text, "expected to find: " + 'Recce is a data validation and review tool for dbt projects. It helps data teams preview, validate, and ship data changes with confidence by providing lineage visualization, data diffing, and collabor'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Pluggable Adapter Pattern**: `BaseAdapter` interface allows support for different data platforms (dbt, SQLMesh). Each adapter implements platform-specific lineage parsing, model retrieval, and SQL' in text, "expected to find: " + '- **Pluggable Adapter Pattern**: `BaseAdapter` interface allows support for different data platforms (dbt, SQLMesh). Each adapter implements platform-specific lineage parsing, model retrieval, and SQL'[:80]

