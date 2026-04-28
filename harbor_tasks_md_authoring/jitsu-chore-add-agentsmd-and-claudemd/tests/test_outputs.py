"""Behavioral checks for jitsu-chore-add-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jitsu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `connectors/` — warehouse connectors (ClickHouse, BigQuery, Redshift, Snowflake, S3,' in text, "expected to find: " + '- `connectors/` — warehouse connectors (ClickHouse, BigQuery, Redshift, Snowflake, S3,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Node.js:** pnpm ≥10 (workspace manager), Turbo (build orchestration), Node.js ≥22' in text, "expected to find: " + '- **Node.js:** pnpm ≥10 (workspace manager), Turbo (build orchestration), Node.js ≥22'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Jitsu is an open-source data pipeline platform (self-hosted Segment alternative). It' in text, "expected to find: " + 'Jitsu is an open-source data pipeline platform (self-hosted Segment alternative). It'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

