"""Behavioral checks for pg-aiguide-update-skills-descriptions-to-match (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pg-aiguide")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/design-postgres-tables/SKILL.md')
    assert '**Keywords:** PostgreSQL schema, table design, data types, PRIMARY KEY, FOREIGN KEY, indexes, B-tree, GIN, JSONB, constraints, normalization, identity columns, partitioning, row-level security' in text, "expected to find: " + '**Keywords:** PostgreSQL schema, table design, data types, PRIMARY KEY, FOREIGN KEY, indexes, B-tree, GIN, JSONB, constraints, normalization, identity columns, partitioning, row-level security'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/design-postgres-tables/SKILL.md')
    assert 'Comprehensive reference covering data types, indexing strategies, constraints, JSONB patterns, partitioning, and PostgreSQL-specific best practices.' in text, "expected to find: " + 'Comprehensive reference covering data types, indexing strategies, constraints, JSONB patterns, partitioning, and PostgreSQL-specific best practices.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/design-postgres-tables/SKILL.md')
    assert '- Design PostgreSQL tables, schemas, or data models when creating new tables and when modifying existing ones.' in text, "expected to find: " + '- Design PostgreSQL tables, schemas, or data models when creating new tables and when modifying existing ones.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-hypertable-candidates/SKILL.md')
    assert 'Provides SQL queries to analyze table statistics, index patterns, and query patterns. Includes scoring criteria (8+ points = good candidate) and pattern recognition for IoT, events, transactions, and ' in text, "expected to find: " + 'Provides SQL queries to analyze table statistics, index patterns, and query patterns. Includes scoring criteria (8+ points = good candidate) and pattern recognition for IoT, events, transactions, and '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-hypertable-candidates/SKILL.md')
    assert '**Keywords:** hypertable candidate, table analysis, migration assessment, Timescale, TimescaleDB, time-series detection, insert-heavy tables, event logs, audit tables' in text, "expected to find: " + '**Keywords:** hypertable candidate, table analysis, migration assessment, Timescale, TimescaleDB, time-series detection, insert-heavy tables, event logs, audit tables'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-hypertable-candidates/SKILL.md')
    assert 'Use this skill to analyze an existing PostgreSQL database and identify which tables should be converted to Timescale/TimescaleDB hypertables.' in text, "expected to find: " + 'Use this skill to analyze an existing PostgreSQL database and identify which tables should be converted to Timescale/TimescaleDB hypertables.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/migrate-postgres-tables-to-hypertables/SKILL.md')
    assert 'Step-by-step migration planning including: partition column selection, chunk interval calculation, PK/constraint handling, migration execution (in-place vs blue-green), and performance validation quer' in text, "expected to find: " + 'Step-by-step migration planning including: partition column selection, chunk interval calculation, PK/constraint handling, migration execution (in-place vs blue-green), and performance validation quer'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/migrate-postgres-tables-to-hypertables/SKILL.md')
    assert '**Keywords:** migrate to hypertable, convert table, Timescale, TimescaleDB, blue-green migration, in-place conversion, create_hypertable, migration validation, compression setup' in text, "expected to find: " + '**Keywords:** migrate to hypertable, convert table, Timescale, TimescaleDB, blue-green migration, in-place conversion, create_hypertable, migration validation, compression setup'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/migrate-postgres-tables-to-hypertables/SKILL.md')
    assert 'Use this skill to migrate identified PostgreSQL tables to Timescale/TimescaleDB hypertables with optimal configuration and validation.' in text, "expected to find: " + 'Use this skill to migrate identified PostgreSQL tables to Timescale/TimescaleDB hypertables with optimal configuration and validation.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pgvector-semantic-search/SKILL.md')
    assert 'Covers: halfvec storage, HNSW index configuration (m, ef_construction, ef_search), quantization strategies, filtered search, bulk loading, and performance tuning.' in text, "expected to find: " + 'Covers: halfvec storage, HNSW index configuration (m, ef_construction, ef_search), quantization strategies, filtered search, bulk loading, and performance tuning.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pgvector-semantic-search/SKILL.md')
    assert '**Keywords:** pgvector, embeddings, semantic search, vector similarity, HNSW, IVFFlat, halfvec, cosine distance, nearest neighbor, RAG, LLM, AI search' in text, "expected to find: " + '**Keywords:** pgvector, embeddings, semantic search, vector similarity, HNSW, IVFFlat, halfvec, cosine distance, nearest neighbor, RAG, LLM, AI search'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pgvector-semantic-search/SKILL.md')
    assert 'Use this skill for setting up vector similarity search with pgvector for AI/ML embeddings, RAG applications, or semantic search.' in text, "expected to find: " + 'Use this skill for setting up vector similarity search with pgvector for AI/ML embeddings, RAG applications, or semantic search.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-hybrid-text-search/SKILL.md')
    assert 'Covers: pg_textsearch BM25 index setup, parallel query patterns, client-side RRF fusion (Python/TypeScript), weighting strategies, and optional ML reranking.' in text, "expected to find: " + 'Covers: pg_textsearch BM25 index setup, parallel query patterns, client-side RRF fusion (Python/TypeScript), weighting strategies, and optional ML reranking.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-hybrid-text-search/SKILL.md')
    assert '**Keywords:** hybrid search, BM25, pg_textsearch, RRF, reciprocal rank fusion, keyword search, full-text search, reranking, cross-encoder' in text, "expected to find: " + '**Keywords:** hybrid search, BM25, pg_textsearch, RRF, reciprocal rank fusion, keyword search, full-text search, reranking, cross-encoder'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/postgres-hybrid-text-search/SKILL.md')
    assert 'Use this skill to implement hybrid search combining BM25 keyword search with semantic vector search using Reciprocal Rank Fusion (RRF).' in text, "expected to find: " + 'Use this skill to implement hybrid search combining BM25 keyword search with semantic vector search using Reciprocal Rank Fusion (RRF).'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert 'Use this skill when creating database schemas or tables for Timescale, TimescaleDB, TigerData, or Tiger Cloud, especially for time-series, IoT, metrics, events, or log data. Use this to improve the pe' in text, "expected to find: " + 'Use this skill when creating database schemas or tables for Timescale, TimescaleDB, TigerData, or Tiger Cloud, especially for time-series, IoT, metrics, events, or log data. Use this to improve the pe'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert '**Keywords:** CREATE TABLE, hypertable, Timescale, TimescaleDB, time-series, IoT, metrics, sensor data, compression policy, continuous aggregates, columnstore, retention policy, chunk interval, segmen' in text, "expected to find: " + '**Keywords:** CREATE TABLE, hypertable, Timescale, TimescaleDB, time-series, IoT, metrics, sensor data, compression policy, continuous aggregates, columnstore, retention policy, chunk interval, segmen'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert 'Step-by-step instructions for hypertable creation, column selection, compression policies, retention, continuous aggregates, and indexes.' in text, "expected to find: " + 'Step-by-step instructions for hypertable creation, column selection, compression policies, retention, continuous aggregates, and indexes.'[:80]

