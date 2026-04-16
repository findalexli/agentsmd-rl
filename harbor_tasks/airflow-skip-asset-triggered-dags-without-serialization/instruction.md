# Fix Scheduler: Skip Asset-Triggered DAGs Without SerializedDagModel

## Problem

When the Airflow scheduler processes DAGs with queued asset events (`AssetDagRunQueue` rows), it may attempt to create DagRuns for DAGs that don't yet have a `SerializedDagModel` entry. This causes incorrect scheduling behavior — the scheduler acts on DAGs that haven't been serialized yet, which can lead to errors or premature scheduling.

Specifically, when a DAG has `AssetDagRunQueue` rows but no corresponding `SerializedDagModel`, the current code still includes that DAG in the `triggered_date_by_dag` dictionary returned by `DagModel.dags_needing_dagruns()`. This is wrong: DAGs without serialized data should not be considered ready for DagRun creation.

## What to Fix

Modify `airflow-core/src/airflow/models/dag.py` — the `DagModel.dags_needing_dagruns()` method — so that:

- A DAG with `AssetDagRunQueue` rows but no `SerializedDagModel` row is **not included** in the returned `triggered_date_by_dag` dictionary.
- The `AssetDagRunQueue` rows themselves are **NOT deleted** — they remain in the database so the scheduler can re-evaluate the DAG on a future run once serialization has occurred.
- An `INFO`-level log message is emitted when DAGs are skipped due to missing serialized data. The log message must contain the exact text:

  ```
  Dags have queued asset events (ADRQ), but are not found in the serialized_dag table.
  ```

  The message should include the IDs of the skipped DAGs, sorted alphabetically.

## What to Add

Add two new test methods to `airflow-core/tests/unit/models/test_dag.py` in the `TestDagModel` class. These tests must have **exactly** these names:

1. `test_dags_needing_dagruns_skips_adrq_when_serialized_dag_missing` — Verifies that:
   - A DAG with `AssetDagRunQueue` row but no `SerializedDagModel` row does NOT appear in `triggered_date_by_dag`
   - The `AssetDagRunQueue` row IS still present in the database after the call
   - The log message containing `"Dags have queued asset events (ADRQ), but are not found in the serialized_dag table."` is emitted, and the DAG ID appears in the log

2. `test_dags_needing_dagruns_missing_serialized_debug_lists_sorted_dag_ids` — Verifies that:
   - When multiple DAGs have `AssetDagRunQueue` rows but no `SerializedDagModel`, none appear in `triggered_date_by_dag`
   - The log message lists the DAG IDs in alphabetical order (e.g., `ghost_a` appears before `ghost_z`)
   - All `AssetDagRunQueue` rows are preserved in the database

## Important Constraints

- Do **not** call `session.commit()` inside the `dags_needing_dagruns()` method
- The existing tests `test_dags_needing_dagruns_not_too_early` and `test_dags_needing_dagruns_only_unpaused` must continue to pass
- All linting (`ruff`) and type checking (`mypy`) must pass on the modified `dag.py` file