"""Behavioral checks for posthog-feat-add-clickhouse-migration-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `[NodeRole.DATA, NodeRole.COORDINATOR]`: Non-sharded data tables, distributed read tables, replicated tables, views, dictionaries' in text, "expected to find: " + '- `[NodeRole.DATA, NodeRole.COORDINATOR]`: Non-sharded data tables, distributed read tables, replicated tables, views, dictionaries'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See `posthog/clickhouse/migrations/AGENTS.md` for comprehensive patterns, examples, and ingestion layer setup' in text, "expected to find: " + 'See `posthog/clickhouse/migrations/AGENTS.md` for comprehensive patterns, examples, and ingestion layer setup'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When dropping and recreating replicated table in same migration, use `DROP TABLE IF EXISTS ... SYNC`' in text, "expected to find: " + '- When dropping and recreating replicated table in same migration, use `DROP TABLE IF EXISTS ... SYNC`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('posthog/clickhouse/migrations/AGENTS.md')
    assert 'The `SYNC` modifier ensures the drop completes before the subsequent CREATE runs - this is necessary becasue replicated table keeps' in text, "expected to find: " + 'The `SYNC` modifier ensures the drop completes before the subsequent CREATE runs - this is necessary becasue replicated table keeps'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('posthog/clickhouse/migrations/AGENTS.md')
    assert 'The recommended pattern for new tables uses dedicated ingestion nodes. This separates ingestion load from query load.' in text, "expected to find: " + 'The recommended pattern for new tables uses dedicated ingestion nodes. This separates ingestion load from query load.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('posthog/clickhouse/migrations/AGENTS.md')
    assert '2. Create writable distributed table on ingestion nodes with `CLICKHOUSE_SINGLE_SHARD_CLUSTER` for non-sharded tables' in text, "expected to find: " + '2. Create writable distributed table on ingestion nodes with `CLICKHOUSE_SINGLE_SHARD_CLUSTER` for non-sharded tables'[:80]

