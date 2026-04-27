"""Behavioral checks for agents-use-af-cli-in-skills (markdown_authoring task).

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
    text = _read('skills/airflow/SKILL.md')
    assert '- "What depends on this table?" / "What breaks if I change this?" -> use the **tracing-downstream-lineage** skill' in text, "expected to find: " + '- "What depends on this table?" / "What breaks if I change this?" -> use the **tracing-downstream-lineage** skill'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/airflow/SKILL.md')
    assert '- "Is the data fresh?" / "When was this table last updated?" -> use the **checking-freshness** skill' in text, "expected to find: " + '- "Is the data fresh?" / "When was this table last updated?" -> use the **checking-freshness** skill'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/airflow/SKILL.md')
    assert '| **tracing-downstream-lineage** | Impact analysis -- what breaks if something changes |' in text, "expected to find: " + '| **tracing-downstream-lineage** | Impact analysis -- what breaks if something changes |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/authoring-dags/SKILL.md')
    assert '> **For testing and debugging DAGs**, see the **testing-dags** skill which covers the full test -> debug -> fix -> retest workflow.' in text, "expected to find: " + '> **For testing and debugging DAGs**, see the **testing-dags** skill which covers the full test -> debug -> fix -> retest workflow.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/authoring-dags/SKILL.md')
    assert '> **Testing commands** -- See the **testing-dags** skill for `af runs trigger-wait`, `af runs diagnose`, `af tasks logs`, etc.' in text, "expected to find: " + '> **Testing commands** -- See the **testing-dags** skill for `af runs trigger-wait`, `af runs diagnose`, `af tasks logs`, etc.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/authoring-dags/SKILL.md')
    assert 'This skill guides you through creating and validating Airflow DAGs using best practices and `af` CLI commands.' in text, "expected to find: " + 'This skill guides you through creating and validating Airflow DAGs using best practices and `af` CLI commands.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/checking-freshness/SKILL.md')
    assert '1. **Find the DAG**: Which DAG populates this table? Use `af dags list` and look for matching names.' in text, "expected to find: " + '1. **Find the DAG**: Which DAG populates this table? Use `af dags list` and look for matching names.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/checking-freshness/SKILL.md')
    assert '- Is the DAG paused? Use `af dags get <dag_id>`' in text, "expected to find: " + '- Is the DAG paused? Use `af dags get <dag_id>`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/checking-freshness/SKILL.md')
    assert '- Did the last run fail? Use `af dags stats`' in text, "expected to find: " + '- Did the last run fail? Use `af dags stats`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-dags/SKILL.md')
    assert 'Use `af runs get <dag_id> <dag_run_id>` to compare the failed run against recent successful runs.' in text, "expected to find: " + 'Use `af runs get <dag_id> <dag_run_id>` to compare the failed run against recent successful runs.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-dags/SKILL.md')
    assert '- To clear and rerun failed tasks: `af tasks clear <dag_id> <run_id> <task_ids> -D`' in text, "expected to find: " + '- To clear and rerun failed tasks: `af tasks clear <dag_id> <run_id> <task_ids> -D`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/debugging-dags/SKILL.md')
    assert 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.' in text, "expected to find: " + 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing-dags/SKILL.md')
    assert 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.' in text, "expected to find: " + 'Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing-dags/SKILL.md')
    assert 'uvx --from astro-airflow-mcp af <command>' in text, "expected to find: " + 'uvx --from astro-airflow-mcp af <command>'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-downstream-lineage/SKILL.md')
    assert '1. **Check what the DAG produces**: Use `af dags source <dag_id>` to find output tables' in text, "expected to find: " + '1. **Check what the DAG produces**: Use `af dags source <dag_id>` to find output tables'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-downstream-lineage/SKILL.md')
    assert '- Use `af dags source <dag_id>` to search for table references' in text, "expected to find: " + '- Use `af dags source <dag_id>` to search for table references'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-downstream-lineage/SKILL.md')
    assert '- Use `af dags list` to get all DAGs' in text, "expected to find: " + '- Use `af dags list` to get all DAGs'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-upstream-lineage/SKILL.md')
    assert '1. **Search DAGs by name**: Use `af dags list` and look for DAG names matching the table name' in text, "expected to find: " + '1. **Search DAGs by name**: Use `af dags list` and look for DAG names matching the table name'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-upstream-lineage/SKILL.md')
    assert '3. **Check DAG tasks**: Use `af tasks list <dag_id>` to see what operations the DAG performs' in text, "expected to find: " + '3. **Check DAG tasks**: Use `af tasks list <dag_id>` to see what operations the DAG performs'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tracing-upstream-lineage/SKILL.md')
    assert '2. **Explore DAG source code**: Use `af dags source <dag_id>` to read the DAG definition' in text, "expected to find: " + '2. **Explore DAG source code**: Use `af dags source <dag_id>` to read the DAG definition'[:80]

