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

## Required Code Patterns

The fix must include the following exact code patterns for the session renewal mechanism to work correctly:

1. A local variable declaration: `zkutil::ZooKeeperPtr current_zookeeper = zookeeper;`
2. A retry check inside the retry loop: `if (retries_ctl.isRetry())`
3. A session renewal call: `zookeeper_getter.getZooKeeper().first;`
4. `tryLoadObject` must be called with `current_zookeeper` (not the original `zookeeper` parameter)
5. `getObjectNamesAndSetWatch` must be called with `current_zookeeper`

## Code Style Requirements

The fix must follow ClickHouse coding standards:

1. **Allman brace style** - Opening braces for control structures (if, for, while, etc.) must be on a new line
2. **No tabs** - Use spaces for indentation
3. **No sleep calls** - Never use `sleep()`, `usleep()`, or `std::this_thread::sleep_for()` for synchronization or race condition handling
4. **Use LOG_* macros** - Use ClickHouse logging macros (LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR) instead of std::cout/std::cerr
5. **No raw assert()** - Use CH_ASSERT or other ClickHouse assertion mechanisms
6. **Comments** - Code comments must reference the `zookeeper_getter` mechanism and include one of the terms `renew`, `expired`, or `fresh` to document the session handling behavior
