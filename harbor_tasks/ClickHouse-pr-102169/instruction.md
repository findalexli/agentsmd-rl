# Fix Crash: Stale ZooKeeper Session in UDF Retry Loop

## Problem Description

The `refreshObjects` method in `UserDefinedSQLObjectsZooKeeperStorage` has a bug where the `ZooKeeperRetriesControl` retry loop reuses the same expired ZooKeeper session on every retry iteration. This causes crashes when the session becomes stale (expired) but the code continues to use it.

The issue is in `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp` in the `refreshObjects` function.

## What's Broken

1. The function receives a `zookeeper` parameter (a ZooKeeper session handle)
2. `getObjectNamesAndSetWatch()` is called with this handle BEFORE the retry loop
3. Inside the `ZooKeeperRetriesControl::retryLoop` lambda, the same `zookeeper` handle is used
4. If the session expires during retries, the code continues using the stale handle
5. This leads to crashes when trying to use a finalized/invalid session

## Expected Behavior

When a retry is triggered (because of a ZooKeeper error), the code must:
1. Check if this is a retry iteration using `retries_ctl.isRetry()`
2. If so, obtain a fresh ZooKeeper session via `zookeeper_getter.getZooKeeper()`
3. Re-fetch the object list using the fresh session so watches are set correctly
4. Use the fresh session handle for all ZooKeeper operations in that iteration

## Key Files

- `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp` - Contains the `refreshObjects` method

## Pattern to Follow

Look at other retry loops in the ClickHouse codebase (e.g., backup coordination code). They follow this pattern:

```cpp
ZooKeeperPtr current_zookeeper = zookeeper;  // Start with provided handle

retries_ctl.retryLoop([&] {
    if (retries_ctl.isRetry())
        current_zookeeper = zookeeper_getter.getZooKeeper().first;  // Renew on retry

    // Use current_zookeeper for all operations...
});
```

## Agent Notes

- The function `getObjectNamesAndSetWatch` needs to be INSIDE the retry loop, not before it
- The variable `zookeeper` (parameter) should not be used directly inside the loop - use a local `current_zookeeper` variable instead
- Update the comments to explain the new behavior
- Follow the existing ClickHouse code style
- When referring to logical errors, use "exception" rather than "crash" (per CLAUDE.md conventions)
