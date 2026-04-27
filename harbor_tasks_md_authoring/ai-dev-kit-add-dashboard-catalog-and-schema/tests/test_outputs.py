"""Behavioral checks for ai-dev-kit-add-dashboard-catalog-and-schema (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-dev-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/asset-bundles/SKILL.md')
    assert '| **Hardcoded catalog in dashboard** | Use dataset_catalog parameter (CLI v0.281.0+), create environment-specific files, or parameterize JSON |' in text, "expected to find: " + '| **Hardcoded catalog in dashboard** | Use dataset_catalog parameter (CLI v0.281.0+), create environment-specific files, or parameterize JSON |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/asset-bundles/SKILL.md')
    assert 'dataset_catalog: ${var.catalog} # Default catalog used by all datasets in the dashboard if not otherwise specified in the query' in text, "expected to find: " + 'dataset_catalog: ${var.catalog} # Default catalog used by all datasets in the dashboard if not otherwise specified in the query'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/asset-bundles/SKILL.md')
    assert 'dataset_schema: ${var.schema} # Default schema used by all datasets in the dashboard if not otherwise specified in the query' in text, "expected to find: " + 'dataset_schema: ${var.schema} # Default schema used by all datasets in the dashboard if not otherwise specified in the query'[:80]

