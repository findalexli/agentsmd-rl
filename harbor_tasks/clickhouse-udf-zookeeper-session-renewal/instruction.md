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

The bug is in the retry loop that refreshes user-defined SQL objects from ZooKeeper. Currently, `object_names` is fetched once before the retry loop begins, and the same `zookeeper` session handle is used throughout all retry iterations.

## Expected Fix

The fix should:

1. **Move `getObjectNamesAndSetWatch` inside the retry loop** - So that object list and watches are re-established on a fresh session each retry

2. **Renew the ZooKeeper session on each retry** - Use `zookeeper_getter.getZooKeeper().first` to obtain a fresh session when `retries_ctl.isRetry()` is true

3. **Use a `current_zookeeper` variable** - Instead of the function parameter `zookeeper`, use a local variable that can be updated with the fresh session on retry

4. **Follow ClickHouse code style** - Use Allman-style braces (opening brace on new line)

5. **Never use sleep** for synchronization - This is explicitly forbidden by ClickHouse coding rules

## Pattern Reference

This fix follows the same pattern used by backup coordination code and other retry loops in the ClickHouse codebase. When retrying ZooKeeper operations:

- Check if this is a retry iteration via the retries control object
- If so, obtain a fresh ZooKeeper session via the getter
- Re-fetch any watches/state needed on the new session
- Use the fresh session for all operations in that iteration

## Testing

The fix should ensure that:
- The code compiles correctly
- Session renewal happens inside the retry loop
- All ZooKeeper operations use the potentially-refreshed session handle
- Code follows ClickHouse style rules
