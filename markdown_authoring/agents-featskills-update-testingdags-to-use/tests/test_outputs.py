"""Behavioral checks for agents-featskills-update-testingdags-to-use (markdown_authoring task).

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
    text = _read('skills/testing-dags/SKILL.md')
    assert 'If a task shows `upstream_failed`, the root cause is in an upstream task. Use `af runs diagnose` to find which task actually failed.' in text, "expected to find: " + 'If a task shows `upstream_failed`, the root cause is in an upstream task. Use `af runs diagnose` to find which task actually failed.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing-dags/SKILL.md')
    assert 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp@latest af`.' in text, "expected to find: " + 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp@latest af`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing-dags/SKILL.md')
    assert 'af runs trigger-wait my_dag --conf \'{"env": "staging", "batch_size": 100}\' --timeout 600' in text, "expected to find: " + 'af runs trigger-wait my_dag --conf \'{"env": "staging", "batch_size": 100}\' --timeout 600'[:80]

