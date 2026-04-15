# Fix Crash in UDF Refresh Due to Stale ZooKeeper Session

## Problem

The `refreshObjects` function in `UserDefinedSQLObjectsZooKeeperStorage.cpp` crashes when transient ZooKeeper/Keeper hiccups occur. The `ZooKeeperRetriesControl` retry loop reuses the same expired ZooKeeper session on every retry iteration without renewing it.

When a Keeper connection blip or session jitter occurs:
1. The retry loop attempts to retry the operation
2. But it continues using the old expired session handle
3. This causes repeated requests on a finalized session
4. Leading to server crashes (as seen in production canary deploys)

## Affected Code

**File:** `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

**Function:** `UserDefinedSQLObjectsZooKeeperStorage::refreshObjects`

**Bug Description:** The retry loop that refreshes user-defined SQL objects from ZooKeeper uses a ZooKeeper session handle that was obtained once before the retry loop begins. When `ZooKeeperRetriesControl` triggers a retry due to a transient Keeper error, the code continues using the same potentially-expired session handle instead of obtaining a fresh one. This means each retry iteration repeats the operation with the same stale session, causing crashes when the session has been finalized.

## Expected Behavior

When the retry mechanism triggers a retry iteration:
1. A fresh ZooKeeper session should be obtained via the `zookeeper_getter` mechanism
2. The fresh session should be used for all ZooKeeper operations in that retry iteration
3. Any watches or object lists should be re-established on the fresh session
4. The session renewal must happen inside the retry loop, not outside it

## Code Style Requirements

The fix must follow ClickHouse coding standards:

1. **Allman brace style** - Opening braces for control structures (if, for, while, etc.) must be on a new line
2. **No tabs** - Use spaces for indentation
3. **No sleep calls** - Never use `sleep()`, `usleep()`, or `std::this_thread::sleep_for()` for synchronization or race condition handling
4. **Use LOG_* macros** - Use ClickHouse logging macros (LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR) instead of std::cout/std::cerr
5. **No raw assert()** - Use CH_ASSERT or other ClickHouse assertion mechanisms

## Testing

The fix should ensure that:
- The code compiles correctly
- Session renewal happens inside the retry loop when `retries_ctl.isRetry()` indicates a retry iteration
- All ZooKeeper operations use the session handle that may have been refreshed
- Code follows ClickHouse style rules (Allman braces, no tabs, no sleep calls)
