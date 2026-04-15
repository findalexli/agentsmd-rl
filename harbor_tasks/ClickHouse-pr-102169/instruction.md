# Fix Stale ZooKeeper Session in User-Defined Object Refresh

## Problem

In the ClickHouse codebase (`/workspace/ClickHouse`), the code responsible for refreshing user-defined SQL objects from ZooKeeper has a bug involving stale sessions during retry operations.

The `ZooKeeperRetriesControl` retry mechanism is used for resilience against transient Keeper errors, but the code reuses the same ZooKeeper session handle even after it may have expired. Furthermore, the object name list with watches is fetched before the retry loop begins, so on retry iterations the watches remain tied to the stale session rather than being re-established on a fresh one.

This causes exceptions when a ZooKeeper session expires during a refresh cycle and the code continues operating on the expired handle.

## Acceptance Criteria

The fix must satisfy all of the following:

1. A local variable `current_zookeeper` of type `zkutil::ZooKeeperPtr` must be declared to track the session handle.

2. On retry iterations — detected via `retries_ctl.isRetry()` — the code must obtain a fresh ZooKeeper session through `zookeeper_getter.getZooKeeper()` (the return value is a pair; use `.first` for the handle).

3. The call to `getObjectNamesAndSetWatch()` must appear inside the `retries_ctl.retryLoop` lambda, not before it. This ensures watches are set on the current (potentially renewed) session.

4. Both `tryLoadObject` and `getObjectNamesAndSetWatch` must be called with `current_zookeeper` as the session argument, not the original `zookeeper` parameter.

5. Comments in the modified code must use the word "exception" (not "crash") when referring to logical errors, following project conventions documented in CLAUDE.md.
