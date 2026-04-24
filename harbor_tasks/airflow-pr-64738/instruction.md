# Fix Scheduler Crash with Asset-Triggered DAGs Missing Serialization

## Problem

The Airflow scheduler crashes with a `KeyError` when processing asset-triggered DAGs that have `AssetDagRunQueue` (ADRQ) rows but no corresponding entry in the `serialized_dag` table.

This scenario occurs when:
1. A DAG with asset triggers is parsed and creates ADRQ entries
2. The serialized DAG entry is deleted or never created (e.g., during deployment, file removal, or parsing failure)
3. The scheduler tries to create DAG runs for these orphaned DAGs

## Symptoms

When the scheduler processes asset-triggered DAGs, it builds in-memory dictionaries grouping ADRQ rows and tracking scheduling status. After fetching serialized DAGs from the database, it iterates over the results and accesses the status dictionary by dag_id. If some dag_ids in the ADRQ grouping have no corresponding serialized entry, the access raises a `KeyError`.

## Requirements

Fix the scheduler so that DAGs with ADRQ entries but no serialized representation are gracefully handled:

1. **Detect orphaned DAGs.** After obtaining serialized DAGs from the database, identify which dag_ids have ADRQ entries but are absent from the serialized results. Compute this as a set difference between the dag_ids with ADRQ entries and the dag_ids from serialized DAGs.

2. **Log skipped DAGs.** When orphaned DAGs are detected, emit an INFO-level log message. The message must indicate these DAGs are not found in the serialized_dag table. Log the affected dag_ids in sorted order for deterministic output.

3. **Clean up in-memory state only.** Remove orphaned dag_ids from the in-memory dictionaries that track ADRQ groupings and scheduling status. Do NOT delete any ADRQ database rows — they must persist for re-evaluation on subsequent scheduler runs.

4. **Existing functionality preserved.** DAGs with proper serialization continue to be processed normally.

## Technical Constraints

- Follow Airflow coding standards (no `assert` in production code, `session` parameters are keyword-only and must not call `commit()`)
- Minimal, focused fix
- Must pass `ruff check` and `ruff format --check` linting