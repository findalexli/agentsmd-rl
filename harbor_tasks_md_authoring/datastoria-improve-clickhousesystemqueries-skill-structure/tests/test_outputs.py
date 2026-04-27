"""Behavioral checks for datastoria-improve-clickhousesystemqueries-skill-structure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/datastoria")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/skills/clickhouse-system-queries/SKILL.md')
    assert '2. **Load reference** — for `system.query_log`, call `skill_resource` to load `references/system-query-log.md` before writing any SQL. For unsupported tables, fall back to `sql-expert`.' in text, "expected to find: " + '2. **Load reference** — for `system.query_log`, call `skill_resource` to load `references/system-query-log.md` before writing any SQL. For unsupported tables, fall back to `sql-expert`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/skills/clickhouse-system-queries/SKILL.md')
    assert '1. **Resolve target** — identify system table and intent. Inherit the most recent time window from conversation, or default to last 60 minutes.' in text, "expected to find: " + '1. **Resolve target** — identify system table and intent. Inherit the most recent time window from conversation, or default to last 60 minutes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/skills/clickhouse-system-queries/SKILL.md')
    assert '- If the user named an exact metric, pass it in the `columns` list via `explore_schema` instead of loading the full table schema.' in text, "expected to find: " + '- If the user named an exact metric, pass it in the `columns` list via `explore_schema` instead of loading the full table schema.'[:80]

