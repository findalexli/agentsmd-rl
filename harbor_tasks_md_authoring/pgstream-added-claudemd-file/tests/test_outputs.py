"""Behavioral checks for pgstream-added-claudemd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pgstream")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'pgstream is a PostgreSQL Change Data Capture (CDC) tool and Go library. It captures WAL changes from PostgreSQL and routes them to multiple targets: PostgreSQL, Elasticsearch/OpenSearch, Kafka, or Web' in text, "expected to find: " + 'pgstream is a PostgreSQL Change Data Capture (CDC) tool and Go library. It captures WAL changes from PostgreSQL and routes them to multiple targets: PostgreSQL, Elasticsearch/OpenSearch, Kafka, or Web'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The streaming pipeline is assembled in `pkg/stream/stream.go`. Sources produce WAL events, which flow through an ordered chain of processors before reaching the target writer. Each processor is option' in text, "expected to find: " + 'The streaming pipeline is assembled in `pkg/stream/stream.go`. Sources produce WAL events, which flow through an ordered chain of processors before reaching the target writer. Each processor is option'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Located in `pkg/stream/integration/`. They use testcontainers-go to spin up PostgreSQL, Elasticsearch, OpenSearch, and Kafka. Gated by `PGSTREAM_INTEGRATION_TESTS=true` env var.' in text, "expected to find: " + 'Located in `pkg/stream/integration/`. They use testcontainers-go to spin up PostgreSQL, Elasticsearch, OpenSearch, and Kafka. Gated by `PGSTREAM_INTEGRATION_TESTS=true` env var.'[:80]

