# Fix SQLite Migration 0097 Foreign Key Constraint Failure

## Problem

Migration `0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py` fails when running on SQLite with a `FOREIGN KEY constraint failed` error during the `DROP TABLE dag` operation.

This happens when upgrading from Airflow 3.1.8 to 3.2.0 on an existing SQLite database that has DAG runs and task instances referencing the `dag` table.

## Root Cause

The migration uses the `disable_sqlite_fkeys()` context manager imported from `airflow.migrations.utils` to disable foreign key checks during schema modifications. This context manager executes `PRAGMA foreign_keys=off`.

On SQLite, `PRAGMA foreign_keys=off` is **silently ignored when a transaction is already active**. The migration's `upgrade()` function contains two UPDATE statements:
- `UPDATE log SET event = '' WHERE event IS NULL`
- `UPDATE dag SET is_stale = false WHERE is_stale IS NULL`

These UPDATE statements trigger SQLAlchemy's autobegin, starting a transaction before the `PRAGMA foreign_keys=off` can take effect. As a result, foreign key constraints remain enforced, causing the subsequent `DROP TABLE dag` to fail with a foreign key constraint error.

## Migration Details

The migration file is located at:
`airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py`

The migration uses `with disable_sqlite_fkeys(op):` as a context manager and contains `batch_alter_table("log")` operations.

## Requirements

The migration must use `with disable_sqlite_fkeys(op):` in the `upgrade()` function.

The import statement `from airflow.migrations.utils import disable_sqlite_fkeys` must be present.

Both UPDATE statements (`UPDATE log SET event` and `UPDATE dag SET is_stale`) must be present in the migration.

## Expected Behavior

After the fix, the migration should complete successfully on SQLite without FOREIGN KEY constraint errors, even when existing DAG runs and task instances reference the `dag` table. The data updates should be applied correctly before any schema alterations that require the columns to be non-NULL.
