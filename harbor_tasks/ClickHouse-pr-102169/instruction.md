# Fix Stale ZooKeeper Session in User-Defined Object Refresh

## Problem

In the ClickHouse codebase at `/workspace/ClickHouse`, the user-defined SQL objects ZooKeeper storage implementation (in `src/Functions/UserDefined/`) has a bug in its object refresh logic. When the underlying ZooKeeper session expires mid-operation, the code throws exceptions instead of recovering.

### Symptom

Two related issues cause the failure:

1. **Stale watches**: `getObjectNamesAndSetWatch` is called once *before* the retry loop begins, so watches are bound to a session that may later expire. On retry, operations fail because watches are still attached to the expired session.

2. **Stale session handle**: The `zookeeper` parameter captured at function entry is reused throughout all retry iterations. Even when the underlying session has expired between attempts, the stale handle continues to be used for all ZooKeeper operations.

### Available Infrastructure

The class already provides the tools needed for recovery:

- `zookeeper_getter` — a member whose `getZooKeeper()` method returns `std::pair<ZooKeeperPtr, ...>`. Use `.first` to extract the session pointer.
- `retries_ctl.isRetry()` — detects whether the current retry-loop iteration is a retry (as opposed to the first attempt).
- `retries_ctl.retryLoop(...)` — the retry loop wrapper already in use.

## Requirements

After the fix, the code must satisfy all of the following:

1. The active ZooKeeper session must be tracked in a variable named `current_zookeeper` of type `zkutil::ZooKeeperPtr`, initialized from the original `zookeeper` parameter.

2. On retry iterations (detected via `retries_ctl.isRetry()`), the session-tracking variable must be updated with a fresh session from `zookeeper_getter.getZooKeeper().first`.

3. The `getObjectNamesAndSetWatch` call must be inside the retry loop (not before it), so that watches are always established on the current session.

4. All ZooKeeper operations inside the retry loop — including `tryLoadObject` and `getObjectNamesAndSetWatch` — must use `current_zookeeper` rather than the original `zookeeper` parameter.

5. Per the conventions in `CLAUDE.md`, comments should use the word "exception" (not "crash") when referring to logical errors.
