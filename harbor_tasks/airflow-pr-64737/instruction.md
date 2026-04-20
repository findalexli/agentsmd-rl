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

1. **Use row-level database locking** when querying for expired deadlines, ensuring that once one scheduler replica locks a row, other replicas cannot access that same row until the lock is released.

2. **Skip locked rows rather than blocking** - scheduler replicas should not wait on each other; if a row is already locked by another replica, the query should skip it and move on.

3. **Use a sufficiently strong lock mode** - weaker lock modes like `FOR KEY SHARE` do not conflict with themselves and would still permit concurrent replicas to process the same row. A stronger lock like `FOR UPDATE` is needed.

4. **Target the Deadline model specifically** - the locking must be applied to the `Deadline` table/entity to ensure proper row-level granularity.

5. **Preserve code clarity** - extract the query into a named variable (rather than inline) and add an explanatory comment describing why the locking is necessary (mentioning HA schedulers and prevention of duplicate callbacks).

## Expected Behavior

Each expired deadline should be processed exactly once, regardless of how many scheduler replicas are running.
