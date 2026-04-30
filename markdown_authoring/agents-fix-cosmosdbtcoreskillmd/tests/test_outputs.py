"""Behavioral checks for agents-fix-cosmosdbtcoreskillmd (markdown_authoring task).

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
    text = _read('skills/cosmos-dbt-core/SKILL.md')
    assert '> **Before starting**, confirm: (1) dbt engine = Core (not Fusion → use **cosmos-dbt-fusion**), (2) warehouse type, (3) Airflow version, (4) execution environment (Airflow env / venv / container), (5)' in text, "expected to find: " + '> **Before starting**, confirm: (1) dbt engine = Core (not Fusion → use **cosmos-dbt-fusion**), (2) warehouse type, (3) Airflow version, (4) execution environment (Airflow env / venv / container), (5)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cosmos-dbt-core/SKILL.md')
    assert '| `dbt_ls` | Complex selectors; need dbt-native selection | dbt installed OR `dbt_executable_path` | Can also be used with containerized execution |' in text, "expected to find: " + '| `dbt_ls` | Complex selectors; need dbt-native selection | dbt installed OR `dbt_executable_path` | Can also be used with containerized execution |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cosmos-dbt-core/SKILL.md')
    assert '| `LOCAL` + `SUBPROCESS` | dbt + adapter available in the Airflow deployment, in an isolated Python installation | Medium | `dbt_executable_path` |' in text, "expected to find: " + '| `LOCAL` + `SUBPROCESS` | dbt + adapter available in the Airflow deployment, in an isolated Python installation | Medium | `dbt_executable_path` |'[:80]

