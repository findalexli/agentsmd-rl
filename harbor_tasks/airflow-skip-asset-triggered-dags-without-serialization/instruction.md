# Fix Scheduler: Skip Asset-Triggered DAGs Without SerializedDagModel

## Problem

The Airflow scheduler's `dags_needing_dagruns()` method in `DagModel` has a bug where it incorrectly includes DAGs with queued asset events (`AssetDagRunQueue` rows) even when those DAGs don't have a corresponding `SerializedDagModel` row. This can cause:

1. Premature DagRun creation attempts for DAGs that haven't been serialized yet
2. Potential errors when the scheduler tries to access serialized DAG data that doesn't exist
3. Incorrect scheduling behavior during DAG parsing/serialization race conditions

## Files to Modify

- **`airflow-core/src/airflow/models/dag.py`** - The `DagModel.dags_needing_dagruns()` method

## What You Need to Fix

The `dags_needing_dagruns()` method retrieves `SerializedDagModel` rows for DAGs with `AssetDagRunQueue` entries. Currently, it doesn't handle the case where some DAGs have `AssetDagRunQueue` rows but no `SerializedDagModel` yet.

### Expected Behavior

After fetching the serialized DAGs for the candidate DAGs from `AssetDagRunQueue`, the method should:

1. **Identify and skip orphan DAGs**: Compare the set of DAGs with `AssetDagRunQueue` rows against the set of DAGs that have corresponding `SerializedDagModel` rows. DAGs that appear in the queue but have no serialized data should be excluded from DagRun creation.

   Use a set difference operation to find orphan DAGs. Store the result in a variable named `missing_from_serialized`. For example: `missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids` where `ser_dag_ids` is a set containing the dag_ids from the retrieved serialized DAGs.

2. **Preserve ADRQ rows**: Do NOT delete `AssetDagRunQueue` rows for DAGs that lack serialized data. These rows must remain in the database so the scheduler can re-evaluate on a later run once `SerializedDagModel` exists.

3. **Emit an informative log message**: When skipping DAGs without serialized data, log an INFO message that includes the sorted list of affected DAG IDs. The log message must contain exactly:

   ```
   Dags have queued asset events (ADRQ), but are not found in the serialized_dag table.
   ```

   The message should include the sorted list of DAG IDs that are missing from the serialized table.

4. **Remove from in-memory processing**: Ensure that DAGs without serialized data are removed from the internal data structures used for subsequent processing in the method (so they don't appear in the returned `triggered_date_by_dag` dictionary).

   Specifically, remove the orphan DAG entries from the `adrq_by_dag` dictionary using `del adrq_by_dag[dag_id]` or `adrq_by_dag.pop(dag_id)` for each orphan DAG ID in `missing_from_serialized`.

## Testing Your Fix

Your fix should pass these behavioral checks:

1. **Skip test**: A DAG with `AssetDagRunQueue` but no `SerializedDagModel` should NOT appear in the `triggered_date_by_dag` dict returned by `dags_needing_dagruns()`

2. **Preservation test**: After calling `dags_needing_dagruns()`, the `AssetDagRunQueue` row for the orphan DAG should still exist in the database

3. **Log test**: An INFO log message should be emitted containing the text "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table." and the affected DAG ID

4. **Sorting test**: When multiple DAGs lack `SerializedDagModel`, they should appear sorted alphabetically (e.g., "ghost_a" before "ghost_z") in the log message

5. **Regression test**: The existing `test_dags_needing_dagruns_assets` test in `tests/unit/models/test_dag.py` should continue to pass

## Key Considerations

- The fix should only affect the in-memory processing data structures, not delete database rows
- Be careful with the session parameter — don't call `session.commit()` in this method
- The implementation should use the variable name `missing_from_serialized` to hold the set of DAG IDs that have ADRQ rows but no SerializedDagModel
- The implementation should use `ser_dag_ids` to refer to the set of DAG IDs that have serialized data
