# SQLite Migration 0097 Fails with Foreign Key Constraint Error

## Problem

Migration `0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py` fails when running on SQLite databases that contain existing data with foreign key relationships.

The error occurs with the message:
```
FOREIGN KEY constraint failed
```

## Technical Context

- The migration is located at `airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py`
- The migration enforces NOT NULL constraints on the `log.event` and `dag.is_stale` columns using `batch_alter_table` and `alter_column("event", ...)` with `nullable=False`
- The migration contains these statements to prepare existing data:
  - `UPDATE log SET event = '' WHERE event IS NULL`
  - `UPDATE dag SET is_stale = false WHERE is_stale IS NULL`
- The migration uses a `disable_sqlite_fkeys` context manager that executes `PRAGMA foreign_keys=OFF`
- SQLite has a critical behavior: `PRAGMA foreign_keys=OFF` is silently ignored if a transaction is already active

## Your Task

Fix the migration file so that it completes successfully on SQLite databases with existing data that has foreign key relationships. The migration must continue to:
1. Prepare existing NULL data in the `log.event` column by setting it to an empty string
2. Prepare existing NULL data in the `dag.is_stale` column by setting it to false
3. Enforce NOT NULL constraints on both columns using batch_alter_table

The file at `airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py` must pass syntax validation and maintain all required migration structure elements.