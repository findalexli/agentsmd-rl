## Problem

Migration 0097 (`0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py`) fails on SQLite with a foreign key constraint error when running `DROP TABLE` operations as part of `batch_alter_table`.

The migration has an `upgrade()` function that needs to:
1. Update existing rows in the `log` table to set `event = ''` where it's NULL
2. Update existing rows in the `dag` table to set `is_stale = false` where it's NULL
3. Alter both tables to make these columns NOT NULL

The `batch_alter_table` operations on SQLite require foreign keys to be temporarily disabled using the `disable_sqlite_fkeys()` context manager. This context manager issues `PRAGMA foreign_keys=off` when entering and `PRAGMA foreign_keys=on` when exiting.

## The Issue

SQLite has a specific behavior: `PRAGMA foreign_keys=off` is silently ignored when executed inside an active transaction. SQLAlchemy's `op.execute()` triggers autobegin, which starts a transaction before the PRAGMA runs.

## Relevant Files

- `airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py` - The migration file with the bug
- `airflow-core/src/airflow/migrations/utils.py` - Contains the `disable_sqlite_fkeys()` context manager

## Your Task

Fix the `upgrade()` function in migration 0097 so that it works correctly on SQLite. The fix should ensure that `PRAGMA foreign_keys=off` executes before any autobegin transaction starts.

Consider what operations should happen inside vs outside the `with disable_sqlite_fkeys(op):` block.
