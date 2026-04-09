# Fix Stale ZooKeeper Session in UDF Refresh Loop

## Problem

The `UserDefinedSQLObjectsZooKeeperStorage::refreshObjects()` function in ClickHouse has a bug where it may use a stale ZooKeeper session handle during retry operations.

When transient ZooKeeper/Keeper errors occur (session expiration, connection blips), the code should:
1. Obtain a fresh ZooKeeper session via the `zookeeper_getter`
2. Re-fetch the object list with watches set on the **live** session
3. Retry the operation with the new session

Currently, the code fetches the object list (`getObjectNamesAndSetWatch`) **before** entering the retry loop. If the session expires during the retry, watches are set on a dead session and the refresh operation fails.

## Target File

`src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

Look at the `refreshObjects()` method and the `ZooKeeperRetriesControl` usage.

## Symptoms

- User-defined functions (UDFs) may not refresh properly when ZooKeeper has transient issues
- Watches may be set on expired sessions, causing missed updates
- The retry logic may not actually recover from session expiration

## Requirements

1. **Session renewal**: On retry, obtain a fresh ZooKeeper session from `zookeeper_getter`
2. **Object list re-fetch**: Call `getObjectNamesAndSetWatch()` inside the retry loop with the current session
3. **Use current session**: Ensure `tryLoadObject()` uses the current (potentially renewed) session, not the stale parameter
4. **No sleep-based fixes**: Do not use `sleep()` to fix race conditions

## Hints

- The function receives a `zookeeper` parameter, but this may become stale
- There's a `zookeeper_getter` member that can provide fresh sessions
- The `ZooKeeperRetriesControl::retryLoop()` provides a way to detect retries via `isRetry()`
- Moving the object name fetching inside the retry loop is key

## Style Requirements

Follow the ClickHouse codebase conventions:
- Use Allman-style braces (opening brace on a new line)
- Do not use `sleep()` for race conditions
