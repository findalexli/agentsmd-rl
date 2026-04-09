# Fix crash caused by stale ZooKeeper session in UDF retry loop

## Problem

The `UserDefinedSQLObjectsZooKeeperStorage::refreshObjects` function in ClickHouse has a critical bug where it reuses an expired ZooKeeper session when retrying after transient Keeper hiccups. This causes crashes on deployments when the ZooKeeper session expires between retries.

## Location

File: `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

Function: `refreshObjects`

## Symptom

The `refreshObjects` function uses `ZooKeeperRetriesControl` to handle transient ZooKeeper connection issues with automatic retry and backoff. However, the retry loop has a flaw:

1. The function receives a `zookeeper` parameter at the start
2. The retry loop uses this same handle on every iteration
3. If the ZooKeeper session expires during a retry attempt, subsequent retries still use the stale session
4. This leads to crashes when operations are attempted on a finalized (expired) session

## Expected Behavior

On each retry iteration, the code should:
1. Check if this is a retry attempt (not the first attempt)
2. If it is a retry, obtain a fresh ZooKeeper session via the `zookeeper_getter`
3. Use the fresh session for subsequent operations
4. Ensure watches are re-established on the live session

## Implementation Notes

The pattern used elsewhere in the ClickHouse codebase for this scenario:
- Use a `current_zookeeper` variable that starts with the initial `zookeeper` parameter
- Inside the retry loop, check `retries_ctl.isRetry()` and if true, renew the session via `zookeeper_getter.getZooKeeper().first`
- Move operations that need fresh sessions (like `getObjectNamesAndSetWatch`) inside the retry loop
- Use `current_zookeeper` instead of the original `zookeeper` parameter for all ZooKeeper operations inside the loop

## Relevant Code Structure

The `refreshObjects` function has a retry loop that looks approximately like:

```cpp
void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects(const zkutil::ZooKeeperPtr & zookeeper, ...)
{
    // Currently: object names fetched here (before retry loop)
    Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);

    // Retry control setup
    ZooKeeperRetriesControl retries_ctl(...);

    retries_ctl.retryLoop([&]
    {
        // Currently: uses the same zookeeper handle on every retry
        for (const auto & function_name : object_names)
        {
            if (auto ast = tryLoadObject(zookeeper, ...))
                ...
        }
    });
}
```

The fix should ensure session renewal happens inside the retry loop and the object list fetching is moved inside so watches are set on the fresh session.

## Code Style

- Use Allman-style braces (opening brace on a new line)
- Write function names in comments as `func` not `func()` for mathematical purity
