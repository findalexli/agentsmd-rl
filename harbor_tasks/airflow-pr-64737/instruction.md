# Fix Duplicate Deadline Callbacks in HA Scheduler Deployments

## Problem

In high-availability (HA) deployments with multiple scheduler replicas, deadline breach callbacks are being executed multiple times for the same deadline. Users report receiving duplicate notifications when a DAG run misses its deadline.

## Symptoms

- Same deadline triggers multiple callbacks (2x, 3x, or more depending on replica count)
- Duplicate `Trigger` records are created in the database for a single missed deadline
- The issue only occurs in HA deployments with multiple concurrent scheduler processes
- Single-scheduler deployments work correctly

## Analysis

The scheduler processes expired deadlines by iterating over unhandled `Deadline` rows from the database. In the file `airflow-core/src/airflow/jobs/scheduler_job_runner.py`, the deadline query does not employ any form of row-level locking. When multiple scheduler replicas run simultaneously, each replica's query returns the same set of unhandled rows, and each replica independently invokes `handle_miss()`, producing duplicate callbacks.

## Requirements

The fix must ensure that each expired deadline row is processed by exactly one scheduler replica by adding row-level locking to the deadline query.

Airflow provides a `with_row_locks` utility in `airflow.utils.sqlalchemy` for applying database-appropriate row-level locking. The deadline query must be wrapped with this utility, configured with the following parameters:

- **`of=Deadline`** — the lock must target the Deadline model specifically for proper row-level granularity
- **`session=session`** — the current database session must be passed so the utility can detect the database dialect and apply the appropriate locking strategy
- **`skip_locked=True`** — rows already locked by another transaction must be skipped rather than causing the query to block, so scheduler replicas do not wait on each other
- **`key_share=False`** — the weaker `FOR KEY SHARE` lock mode must not be used, as it does not conflict with itself and would still permit concurrent replicas to process the same row

The `select(Deadline)` query must be assigned to a variable named `deadline_query` rather than being written inline within `session.scalars()`. A comment should be placed near the locking code that mentions row locking and explains it prevents concurrent HA scheduler replicas from creating duplicate callbacks.

## Expected Behavior

Each expired deadline should be processed exactly once, regardless of how many scheduler replicas are running.
