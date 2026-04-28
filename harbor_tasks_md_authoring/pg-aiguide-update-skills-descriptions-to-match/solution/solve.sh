#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pg-aiguide

# Idempotency guard
if grep -qF "**Keywords:** PostgreSQL schema, table design, data types, PRIMARY KEY, FOREIGN " "skills/design-postgres-tables/SKILL.md" && grep -qF "Provides SQL queries to analyze table statistics, index patterns, and query patt" "skills/find-hypertable-candidates/SKILL.md" && grep -qF "Step-by-step migration planning including: partition column selection, chunk int" "skills/migrate-postgres-tables-to-hypertables/SKILL.md" && grep -qF "Covers: halfvec storage, HNSW index configuration (m, ef_construction, ef_search" "skills/pgvector-semantic-search/SKILL.md" && grep -qF "Covers: pg_textsearch BM25 index setup, parallel query patterns, client-side RRF" "skills/postgres-hybrid-text-search/SKILL.md" && grep -qF "Use this skill when creating database schemas or tables for Timescale, Timescale" "skills/setup-timescaledb-hypertables/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/design-postgres-tables/SKILL.md b/skills/design-postgres-tables/SKILL.md
@@ -1,6 +1,19 @@
 ---
 name: design-postgres-tables
-description: Comprehensive PostgreSQL-specific table design reference covering data types, indexing, constraints, performance patterns, and advanced features
+description: |
+  Use this skill for general PostgreSQL table design.
+
+  **Trigger when user asks to:**
+  - Design PostgreSQL tables, schemas, or data models when creating new tables and when modifying existing ones.
+  - Choose data types, constraints, or indexes for PostgreSQL
+  - Create user tables, order tables, reference tables, or JSONB schemas
+  - Understand PostgreSQL best practices for normalization, constraints, or indexing
+  - Design update-heavy, upsert-heavy, or OLTP-style tables
+
+
+  **Keywords:** PostgreSQL schema, table design, data types, PRIMARY KEY, FOREIGN KEY, indexes, B-tree, GIN, JSONB, constraints, normalization, identity columns, partitioning, row-level security
+
+  Comprehensive reference covering data types, indexing strategies, constraints, JSONB patterns, partitioning, and PostgreSQL-specific best practices.
 ---
 
 # PostgreSQL Table Design
diff --git a/skills/find-hypertable-candidates/SKILL.md b/skills/find-hypertable-candidates/SKILL.md
@@ -1,6 +1,19 @@
 ---
 name: find-hypertable-candidates
-description: Analyze an existing PostgreSQL database to identify tables that would benefit from conversion to TimescaleDB hypertables
+description: |
+  Use this skill to analyze an existing PostgreSQL database and identify which tables should be converted to Timescale/TimescaleDB hypertables.
+
+  **Trigger when user asks to:**
+  - Analyze database tables for hypertable conversion potential
+  - Identify time-series or event tables in an existing schema
+  - Evaluate if a table would benefit from Timescale/TimescaleDB
+  - Audit PostgreSQL tables for migration to Timescale/TimescaleDB/TigerData
+  - Score or rank tables for hypertable candidacy
+
+
+  **Keywords:** hypertable candidate, table analysis, migration assessment, Timescale, TimescaleDB, time-series detection, insert-heavy tables, event logs, audit tables
+
+  Provides SQL queries to analyze table statistics, index patterns, and query patterns. Includes scoring criteria (8+ points = good candidate) and pattern recognition for IoT, events, transactions, and sequential data.
 ---
 
 # PostgreSQL Hypertable Candidate Analysis
diff --git a/skills/migrate-postgres-tables-to-hypertables/SKILL.md b/skills/migrate-postgres-tables-to-hypertables/SKILL.md
@@ -1,6 +1,20 @@
 ---
 name: migrate-postgres-tables-to-hypertables
-description: Comprehensive guide for migrating PostgreSQL tables to TimescaleDB hypertables with optimal configuration and performance validation
+description: |
+  Use this skill to migrate identified PostgreSQL tables to Timescale/TimescaleDB hypertables with optimal configuration and validation.
+
+  **Trigger when user asks to:**
+  - Migrate or convert PostgreSQL tables to hypertables
+  - Execute hypertable migration with minimal downtime
+  - Plan blue-green migration for large tables
+  - Validate hypertable migration success
+  - Configure compression after migration
+
+  **Prerequisites:** Tables already identified as candidates (use find-hypertable-candidates first if needed)
+
+  **Keywords:** migrate to hypertable, convert table, Timescale, TimescaleDB, blue-green migration, in-place conversion, create_hypertable, migration validation, compression setup
+
+  Step-by-step migration planning including: partition column selection, chunk interval calculation, PK/constraint handling, migration execution (in-place vs blue-green), and performance validation queries.
 ---
 
 # PostgreSQL to TimescaleDB Hypertable Migration
diff --git a/skills/pgvector-semantic-search/SKILL.md b/skills/pgvector-semantic-search/SKILL.md
@@ -1,6 +1,19 @@
 ---
 name: pgvector-semantic-search
-description: pgvector setup and best practices for semantic search with text embeddings in PostgreSQL
+description: |
+  Use this skill for setting up vector similarity search with pgvector for AI/ML embeddings, RAG applications, or semantic search.
+
+  **Trigger when user asks to:**
+  - Store or search vector embeddings in PostgreSQL
+  - Set up semantic search, similarity search, or nearest neighbor search
+  - Create HNSW or IVFFlat indexes for vectors
+  - Implement RAG (Retrieval Augmented Generation) with PostgreSQL
+  - Optimize pgvector performance, recall, or memory usage
+  - Use binary quantization for large vector datasets
+
+  **Keywords:** pgvector, embeddings, semantic search, vector similarity, HNSW, IVFFlat, halfvec, cosine distance, nearest neighbor, RAG, LLM, AI search
+
+  Covers: halfvec storage, HNSW index configuration (m, ef_construction, ef_search), quantization strategies, filtered search, bulk loading, and performance tuning.
 ---
 
 # pgvector for Semantic Search
diff --git a/skills/postgres-hybrid-text-search/SKILL.md b/skills/postgres-hybrid-text-search/SKILL.md
@@ -1,6 +1,19 @@
 ---
 name: postgres-hybrid-text-search
-description: Hybrid search in PostgreSQL combining BM25 keyword search (pg_textsearch) with semantic search (pgvector) using RRF fusion
+description: |
+  Use this skill to implement hybrid search combining BM25 keyword search with semantic vector search using Reciprocal Rank Fusion (RRF).
+
+  **Trigger when user asks to:**
+  - Combine keyword and semantic search
+  - Implement hybrid search or multi-modal retrieval
+  - Use BM25/pg_textsearch with pgvector together
+  - Implement RRF (Reciprocal Rank Fusion) for search
+  - Build search that handles both exact terms and meaning
+
+
+  **Keywords:** hybrid search, BM25, pg_textsearch, RRF, reciprocal rank fusion, keyword search, full-text search, reranking, cross-encoder
+
+  Covers: pg_textsearch BM25 index setup, parallel query patterns, client-side RRF fusion (Python/TypeScript), weighting strategies, and optional ML reranking.
 ---
 
 # Hybrid Text Search
diff --git a/skills/setup-timescaledb-hypertables/SKILL.md b/skills/setup-timescaledb-hypertables/SKILL.md
@@ -1,6 +1,18 @@
 ---
 name: setup-timescaledb-hypertables
-description: 'Step-by-step instructions for designing table schemas and setting up TimescaleDB with hypertables, indexes, compression, retention policies, and continuous aggregates. Instructions for selecting: partition columns, segment_by columns, order_by columns, chunk time interval, real-time aggregation.'
+description: |
+  Use this skill when creating database schemas or tables for Timescale, TimescaleDB, TigerData, or Tiger Cloud, especially for time-series, IoT, metrics, events, or log data. Use this to improve the performance of any insert-heavy table.
+
+  **Trigger when user asks to:**
+  - Create or design SQL schemas/tables AND Timescale/TimescaleDB/TigerData/Tiger Cloud is available
+  - Set up hypertables, compression, retention policies, or continuous aggregates
+  - Configure partition columns, segment_by, order_by, or chunk intervals
+  - Optimize time-series database performance or storage
+  - Create tables for sensors, metrics, telemetry, events, or transaction logs
+
+  **Keywords:** CREATE TABLE, hypertable, Timescale, TimescaleDB, time-series, IoT, metrics, sensor data, compression policy, continuous aggregates, columnstore, retention policy, chunk interval, segment_by, order_by
+
+  Step-by-step instructions for hypertable creation, column selection, compression policies, retention, continuous aggregates, and indexes.
 ---
 
 # TimescaleDB Complete Setup
PATCH

echo "Gold patch applied."
