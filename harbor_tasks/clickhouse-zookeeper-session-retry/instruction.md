# Fix Stale ZooKeeper Session in UDF Retry Loop

## Problem

The `refreshObjects` method in `UserDefinedSQLObjectsZooKeeperStorage` has a bug where it may use a stale ZooKeeper session handle during retries.

When transient ZooKeeper connection issues occur, the retry mechanism in `ZooKeeperRetriesControl` attempts to retry the operation. However, the current implementation calls `getObjectNamesAndSetWatch()` BEFORE entering the retry loop, using the original `zookeeper` parameter. If this session becomes stale/expired during the retry, subsequent operations may fail or cause crashes.

## Expected Behavior

The fix should ensure that:
1. A fresh ZooKeeper session is obtained when retrying after a failure
2. `getObjectNamesAndSetWatch()` is called INSIDE the retry loop (not before it)
3. All ZooKeeper operations within the retry loop use the same (potentially refreshed) session handle
4. The session renewal is explicitly checked via `isRetry()` before obtaining a fresh session

## Relevant Code

The bug is in `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp` in the `refreshObjects` method.

Key components:
- `ZooKeeperRetriesControl` - handles retry logic with backoff
- `zookeeper_getter.getZooKeeper()` - obtains a fresh ZooKeeper session
- `getObjectNamesAndSetWatch()` - must be inside the retry loop
- `tryLoadObject()` - must use the same session handle as `getObjectNamesAndSetWatch()`

## Agent Instructions

When working with this codebase:
- The fix involves moving session-dependent calls inside the retry loop
- Use `current_zookeeper` as a local variable to track the current (possibly refreshed) session
- Ensure the session refresh happens conditionally on `isRetry()`
- Keep the existing retry configuration (max_retries=5, backoff parameters)
- Do not change the overall control flow or error handling behavior

## Testing

After implementing the fix:
1. The code should compile without syntax errors
2. The `getObjectNamesAndSetWatch` call must be inside the `retryLoop` lambda
3. The `isRetry()` check must precede the session refresh
4. Both `getObjectNamesAndSetWatch` and `tryLoadObject` should use the same session handle variable
