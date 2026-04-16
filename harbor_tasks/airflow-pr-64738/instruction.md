# Fix Scheduler Crash with Asset-Triggered DAGs Missing Serialization

## Problem

The Airflow scheduler crashes with a `KeyError` when processing asset-triggered DAGs that have `AssetDagRunQueue` (ADRQ) rows but no corresponding entry in the `serialized_dag` table.

This scenario occurs when:
1. A DAG with asset triggers is parsed and creates ADRQ entries
2. The serialized DAG entry is deleted or never created (e.g., during deployment, file removal, or parsing failure)
3. The scheduler tries to create DAG runs for these orphaned DAGs

## Symptoms

The crash occurs in the scheduler's DAG run creation logic for asset-triggered DAGs. The relevant code maintains:
- A dict grouping ADRQ rows by dag_id
- A dict tracking per-DAG scheduling status
- A collection of serialized DAGs fetched from the database

After fetching serialized DAGs, the code iterates over results and accesses the status dict by dag_id. However, some dag_ids present in the ADRQ grouping and status dicts have no corresponding serialized entry, causing a `KeyError` on access.

## Requirements

Fix the scheduler so that DAGs with ADRQ entries but no serialized representation are gracefully handled:

1. **Detect orphaned DAGs.** After obtaining the serialized DAGs, determine which dag_ids have ADRQ entries but are absent from the serialized results. Compute this using set difference between the ADRQ grouping keys and the serialized dag IDs.

2. **Log skipped DAGs.** When orphaned DAGs are detected, emit an INFO-level log message containing the phrase `"not found in the serialized_dag table"`. Log the affected dag_ids in sorted order for deterministic output.

3. **Clean up in-memory state only.** Remove orphaned dag_ids from the in-memory grouping and status dicts. Do NOT delete any ADRQ database rows — they must persist for re-evaluation on subsequent scheduler runs.

4. **Existing functionality preserved.** DAGs with proper serialization continue to be processed normally.

## Constraints

- Follow Airflow coding standards (no `assert` in production code, `session` parameters are keyword-only and must not call `commit()`)
- Minimal, focused fix
- Must pass `ruff check` and `ruff format --check` linting
