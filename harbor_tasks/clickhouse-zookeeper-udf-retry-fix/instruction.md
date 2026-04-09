# Fix Stale ZooKeeper Session in UDF Retry Loop

## Problem

The `refreshObjects` function in `UserDefinedSQLObjectsZooKeeperStorage.cpp` has a bug where a stale ZooKeeper session handle can be used during retries. When the retry loop executes, it may use an expired ZooKeeper session, leading to crashes or undefined behavior.

## Affected File

- `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

## The Bug

The current code fetches the list of object names **before** entering the `ZooKeeperRetriesControl::retryLoop`. If the ZooKeeper session expires and the retry loop triggers, the code continues using the original (now stale) `zookeeper` parameter and the old `object_names` list.

The specific issues:
1. `Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);` is called before the retry loop
2. Inside the retry loop, `tryLoadObject(zookeeper, ...)` uses the potentially stale session
3. When a retry happens due to session expiration, watches and operations are attempted on the expired session

## Required Fix

Move the object name fetching inside the retry loop and obtain a fresh ZooKeeper session when retrying:

1. Declare `zkutil::ZooKeeperPtr current_zookeeper = zookeeper;` before the retry control setup
2. Inside the `retryLoop` lambda:
   - Check if this is a retry using `retries_ctl.isRetry()`
   - If retrying, obtain a fresh session: `current_zookeeper = zookeeper_getter.getZooKeeper().first;`
   - Fetch object names with the (potentially fresh) session: `Strings object_names = getObjectNamesAndSetWatch(current_zookeeper, object_type);`
   - Use `current_zookeeper` instead of `zookeeper` in `tryLoadObject()` calls
3. Update the comment to explain that the session is renewed on retry

## Expected Behavior

After the fix, when a ZooKeeper operation fails and triggers a retry:
- A fresh ZooKeeper session is obtained via `zookeeper_getter`
- Object names are re-fetched with the new session
- Watches are set on the live session
- Operations use the current valid session handle

This ensures that transient Keeper hiccups (brief connection blips, session jitter) are handled correctly without crashing.

## Implementation Notes

- The `zookeeper_getter` is a member of the class that provides access to fresh ZooKeeper connections
- The `ZooKeeperRetriesControl` class handles the retry logic with backoff
- The fix maintains the existing retry count and backoff parameters (`max_retries = 5`, `initial_backoff_ms = 200`, `max_backoff_ms = 5000`)
