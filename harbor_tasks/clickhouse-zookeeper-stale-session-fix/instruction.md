# Fix stale ZooKeeper session in UDF retry loop

## Problem

The `refreshObjects()` method in `UserDefinedSQLObjectsZooKeeperStorage` has a bug where it captures the `object_names` list and the `zookeeper` session handle **before** the retry loop. When a transient Keeper error occurs and the `ZooKeeperRetriesControl` triggers a retry:

1. The old ZooKeeper session may have expired
2. The `object_names` list may be stale
3. Watches are set on the expired session, not the fresh one

This can lead to crashes or inconsistent state when the system tries to use a stale ZooKeeper session.

## Location

**File**: `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

**Function**: `UserDefinedSQLObjectsZooKeeperStorage::refreshObjects()`

## What needs to change

The fix requires restructuring the retry logic so that:

1. **Move `getObjectNamesAndSetWatch` inside the retry loop** - The object list must be re-fetched on each retry attempt to ensure watches are set on the live session.

2. **Obtain a fresh ZooKeeper session on retry** - When a retry is triggered (detected via `retries_ctl.isRetry()`), get a fresh session handle via `zookeeper_getter.getZooKeeper()`.

3. **Use the fresh session for all operations** - The `tryLoadObject()` calls inside the retry loop should use the current (potentially refreshed) session handle, not the original one passed to the function.

## Key components

- `zookeeper_getter` - A function object that returns a fresh ZooKeeper session
- `retries_ctl` - The `ZooKeeperRetriesControl` object managing the retry loop
- `getObjectNamesAndSetWatch()` - Must be called inside the retry loop
- `tryLoadObject()` - Must use the current session handle

## Hints

- Look for the `retryLoop` lambda in the `refreshObjects` method
- The `zookeeper_getter` is a member variable that can provide a fresh session
- `retries_ctl.isRetry()` tells you if this is a retry attempt
- You'll need to declare a `current_zookeeper` variable to hold the session handle
