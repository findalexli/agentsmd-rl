"""Behavioral checks for lmnr-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lmnr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Laminar is an open-source observability platform for AI agents. It provides OpenTelemetry-native tracing, evaluations, AI monitoring, and SQL access to all data.' in text, "expected to find: " + 'Laminar is an open-source observability platform for AI agents. It provides OpenTelemetry-native tracing, evaluations, AI monitoring, and SQL access to all data.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Database schema is managed with Drizzle ORM. The source of truth is the database itself - do NOT edit schema files directly.' in text, "expected to find: " + 'Database schema is managed with Drizzle ORM. The source of truth is the database itself - do NOT edit schema files directly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**PostgreSQL**, **ClickHouse**, and **Query Engine** are required. Other services have automatic fallbacks:' in text, "expected to find: " + '**PostgreSQL**, **ClickHouse**, and **Query Engine** are required. Other services have automatic fallbacks:'[:80]

