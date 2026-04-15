# Fix Scheduler: Skip Asset-Triggered DAGs Without SerializedDagModel

## Problem

The Airflow scheduler's `dags_needing_dagruns()` method in `DagModel` has a bug where it incorrectly includes DAGs with queued asset events (`AssetDagRunQueue` rows) even when those DAGs don't have a corresponding `SerializedDagModel` row. This can cause:

1. Premature DagRun creation attempts for DAGs that haven't been serialized yet
2. Potential errors when the scheduler tries to access serialized DAG data that doesn't exist
3. Incorrect scheduling behavior during DAG parsing/serialization race conditions

## Files to Modify

- **`airflow-core/src/airflow/models/dag.py`** - The `DagModel.dags_needing_dagruns()` method

## What You Need to Fix

The `dags_needing_dagruns()` method retrieves `SerializedDagModel` rows for DAGs with `AssetDagRunQueue` entries, but it doesn't handle the case where some DAGs have `AssetDagRunQueue` rows but no `SerializedDagModel` yet.

You need to implement logic that:

1. **Filters out DAGs missing from serialized_dag table**: After fetching the serialized DAGs, identify which DAG IDs from `adrq_by_dag` have no corresponding serialized data. Remove these DAGs from both `adrq_by_dag` and `dag_statuses` dictionaries before further processing.

2. **Preserves ADRQ rows**: Do NOT delete `AssetDagRunQueue` rows for missing DAGs. These rows must remain in the database so the scheduler can re-evaluate on a later run once `SerializedDagModel` exists.

3. **Emits an informative log message**: When skipping DAGs without serialized data, log an INFO message that includes the sorted list of affected DAG IDs. The log message must contain exactly:

   ```
   Dags have queued asset events (ADRQ), but are not found in the serialized_dag table.
   ```

## Required Variable Names

Your implementation must include these specific variable names:

- `missing_from_serialized` - A set containing the DAG IDs that are in `adrq_by_dag` but not in the serialized results
- `ser_dag_ids` - A set containing the DAG IDs that were found in `SerializedDagModel`

## Expected Behavior After Fix

1. DAGs with `AssetDagRunQueue` rows but no `SerializedDagModel` are **omitted** from the `triggered_date_by_dag` return value
2. The `AssetDagRunQueue` rows for these DAGs remain in the database (not deleted)
3. An INFO log message is emitted listing the skipped DAG IDs (sorted alphabetically)

## Testing Your Fix

Your fix should pass these behavioral checks:

1. **Skip test**: A DAG with `AssetDagRunQueue` but no `SerializedDagModel` should NOT appear in the `triggered_date_by_dag` dict returned by `dags_needing_dagruns()`

2. **Preservation test**: After calling `dags_needing_dagruns()`, the `AssetDagRunQueue` row for the orphan DAG should still exist in the database

3. **Log test**: An INFO log message should be emitted containing the text "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table." and the affected DAG ID

4. **Sorting test**: When multiple DAGs lack `SerializedDagModel`, they should appear sorted alphabetically (e.g., "ghost_a" before "ghost_z") in the log message

5. **Regression test**: The existing `test_dags_needing_dagruns_assets` test in `tests/unit/models/test_dag.py` should continue to pass

## Key Considerations

- The fix should only affect the in-memory dictionaries (`adrq_by_dag` and `dag_statuses`), not delete database rows
- Be careful with the session parameter — don't call `session.commit()` in this method
