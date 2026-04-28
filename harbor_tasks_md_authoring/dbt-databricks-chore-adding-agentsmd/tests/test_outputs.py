"""Behavioral checks for dbt-databricks-chore-adding-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dbt-databricks")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '_This guide is maintained by the dbt-databricks team. When making significant architectural changes, update this guide to help future agents understand the codebase._' in text, "expected to find: " + '_This guide is maintained by the dbt-databricks team. When making significant architectural changes, update this guide to help future agents understand the codebase._'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This guide helps AI agents quickly understand and work productively with the dbt-databricks adapter codebase.' in text, "expected to find: " + 'This guide helps AI agents quickly understand and work productively with the dbt-databricks adapter codebase.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **User Docs**: [docs.getdbt.com](https://docs.getdbt.com/reference/resource-configs/databricks-configs)' in text, "expected to find: " + '- **User Docs**: [docs.getdbt.com](https://docs.getdbt.com/reference/resource-configs/databricks-configs)'[:80]

