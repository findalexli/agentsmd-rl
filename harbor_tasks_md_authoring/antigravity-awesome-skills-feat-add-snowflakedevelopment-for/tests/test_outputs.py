"""Behavioral checks for antigravity-awesome-skills-feat-add-snowflakedevelopment-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/snowflake-development/SKILL.md')
    assert 'description: "Comprehensive Snowflake development assistant covering SQL best practices, data pipeline design (Dynamic Tables, Streams, Tasks, Snowpipe), Cortex AI functions, Cortex Agents, Snowpark P' in text, "expected to find: " + 'description: "Comprehensive Snowflake development assistant covering SQL best practices, data pipeline design (Dynamic Tables, Streams, Tasks, Snowpipe), Cortex AI functions, Cortex Agents, Snowpark P'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/snowflake-development/SKILL.md')
    assert 'In SQL stored procedures (BEGIN...END blocks), variables and parameters **must** use the colon `:` prefix inside SQL statements. Without it, Snowflake raises "invalid identifier" errors.' in text, "expected to find: " + 'In SQL stored procedures (BEGIN...END blocks), variables and parameters **must** use the colon `:` prefix inside SQL statements. Without it, Snowflake raises "invalid identifier" errors.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/snowflake-development/SKILL.md')
    assert 'You are a Snowflake development expert. Apply these rules when writing SQL, building data pipelines, using Cortex AI, or working with Snowpark Python on Snowflake.' in text, "expected to find: " + 'You are a Snowflake development expert. Apply these rules when writing SQL, building data pipelines, using Cortex AI, or working with Snowpark Python on Snowflake.'[:80]

