"""Behavioral checks for agents-fix-airflowadapter-skill-frontmatter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md')
    assert 'description: Airflow adapter pattern for v2/v3 API compatibility. Use when working with adapters, version detection, or adding new API methods that need to work across Airflow 2.x and 3.x.' in text, "expected to find: " + 'description: Airflow adapter pattern for v2/v3 API compatibility. Use when working with adapters, version detection, or adding new API methods that need to work across Airflow 2.x and 3.x.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md')
    assert 'name: airflow-adapter' in text, "expected to find: " + 'name: airflow-adapter'[:80]

