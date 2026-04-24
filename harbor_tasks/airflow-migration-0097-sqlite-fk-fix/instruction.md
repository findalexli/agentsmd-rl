## Problem

Migration 0097 (`0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py`) fails on SQLite with a foreign key constraint error during `batch_alter_table` operations.

The migration's `upgrade()` function needs to:
1. Update existing rows in the `log` table to set `event = ''` where it's NULL
2. Update existing rows in the `dag` table to set `is_stale = false` where it's NULL
3. Alter both tables to make these columns NOT NULL

The migration uses `batch_alter_table` for the ALTER TABLE operations and the `disable_sqlite_fkeys()` context manager from `airflow-core/src/airflow/migrations/utils.py` to temporarily disable foreign key constraints on SQLite.

## The Issue

The `disable_sqlite_fkeys()` context manager issues `PRAGMA foreign_keys=off` when entering and `PRAGMA foreign_keys=on` when exiting, but the current structure of the `upgrade()` function prevents this from working correctly on SQLite. As a result, the `DROP TABLE` operations triggered by `batch_alter_table` fail with a foreign key constraint error.

## Relevant Files

- `airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py` - The migration file with the bug
- `airflow-core/src/airflow/migrations/utils.py` - Contains the `disable_sqlite_fkeys()` context manager

## Your Task

Fix the `upgrade()` function in migration 0097 so that it works correctly on SQLite, ensuring that foreign key constraints are properly disabled when needed during the migration.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
