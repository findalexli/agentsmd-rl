# Fix Duplicate Deadline Callbacks in HA Scheduler Deployments

## Problem

In high-availability (HA) deployments with multiple scheduler replicas, deadline breach callbacks are being executed multiple times for the same deadline. Users report receiving duplicate notifications when a DAG run misses its deadline.

## Symptoms

- Same deadline triggers multiple callbacks (2x, 3x, or more depending on replica count)
- Duplicate `Trigger` records are created in the database for a single missed deadline
- The issue only occurs in HA deployments with multiple concurrent scheduler processes
- Single-scheduler deployments work correctly

## Analysis

The scheduler processes expired deadlines by iterating over unhandled `Deadline` rows from the database. When multiple scheduler replicas run simultaneously, each replica's query returns the same set of unhandled rows, and each replica independently processes the deadline, producing duplicate callbacks.

This is a classic race condition where multiple concurrent database transactions read the same rows before any of them marks those rows as processed.

## Requirements

Fix the race condition so that each expired deadline is processed by exactly one scheduler replica.

The fix must:

1. **Use row-level database locking** - wrap the Deadline query with a function named `with_row_locks` that applies `FOR UPDATE` row-level locking.

2. **Skip locked rows rather than blocking** - the lock call must include `skip_locked=True` so scheduler replicas skip rows locked by other replicas instead of waiting.

3. **Use exclusive lock mode** - the lock call must include `key_share=False` to ensure the lock mode is exclusive and conflicts with itself, preventing concurrent replicas from processing the same row.

4. **Target the Deadline model** - the lock call must specify `of=Deadline` to apply locking at the Deadline row granularity.

5. **Pass session parameter** - the lock call must receive `session=session` to determine database dialect for appropriate locking behavior.

6. **Extract query to a named variable** - store the Deadline SELECT query in a variable before passing it to the locking function (not inline).

7. **Add an explanatory comment** - include a comment explaining why row locking is needed for HA/concurrent scheduler deployments.

## Implementation Details

- The relevant file is: `airflow-core/src/airflow/jobs/scheduler_job_runner.py`
- The Deadline query to be wrapped is a `select(Deadline)` call chain
- The locking is applied using the `with_row_locks(query, session=session, skip_locked=True, key_share=False, of=Deadline)` pattern

## Expected Behavior

Each expired deadline should be processed exactly once, regardless of how many scheduler replicas are running.
