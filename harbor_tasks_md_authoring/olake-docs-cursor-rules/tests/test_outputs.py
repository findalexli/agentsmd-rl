"""Behavioral checks for olake-docs-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/olake")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/olake.mdc')
    assert '**Stale JAR warning:** If `olake-iceberg-java-writer.jar` exists in the project root, `build.sh` will skip rebuilding entirely and the Go binary will use the stale copy. After rebuilding with Maven, y' in text, "expected to find: " + '**Stale JAR warning:** If `olake-iceberg-java-writer.jar` exists in the project root, `build.sh` will skip rebuilding entirely and the Go binary will use the stale copy. After rebuilding with Maven, y'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/olake.mdc')
    assert 'Parse the JSON output `{"catalog":{...},"type":"CATALOG"}` — extract the catalog object and save as `/tmp/olake-e2e-test/streams.json`. Change `sync_mode` to `"full_refresh, incremental, cdc"` as per ' in text, "expected to find: " + 'Parse the JSON output `{"catalog":{...},"type":"CATALOG"}` — extract the catalog object and save as `/tmp/olake-e2e-test/streams.json`. Change `sync_mode` to `"full_refresh, incremental, cdc"` as per '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/olake.mdc')
    assert "Where `<destination_db>` comes from the stream's `destination_database` field (e.g. `postgres_postgres_public`) and `<table_name>` from `destination_table` (e.g. `test_table`). Verify row count = 5." in text, "expected to find: " + "Where `<destination_db>` comes from the stream's `destination_database` field (e.g. `postgres_postgres_public`) and `<table_name>` from `destination_table` (e.g. `test_table`). Verify row count = 5."[:80]

