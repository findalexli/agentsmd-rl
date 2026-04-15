# Fix stale ZooKeeper session in UDF retry loop

## Problem

In `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`, the `refreshObjects()` method has a bug that causes crashes or inconsistent state when ZooKeeper sessions expire during retry attempts.

### Symptom

The method captures the ZooKeeper session handle and the list of object names *before* entering the retry loop. When a transient Keeper error triggers a retry:

- The ZooKeeper session may have expired between the first attempt and the retry
- The cached object names list is stale
- Watches set on the expired session are invalid for the new session

This means the retry operates on an expired session with stale data, leading to crashes or incorrect behavior.

## Expected behavior

After the fix, the following should hold:

- Object names and watches must be fetched using a live ZooKeeper session, not one captured before retries began
- When a retry occurs, a fresh ZooKeeper session should be obtained and used for all subsequent operations within the retry loop
- `tryLoadObject()` calls within the retry loop should use the current (potentially refreshed) session handle, not the stale one originally passed to the method

## Code context

The `refreshObjects()` method in `UserDefinedSQLObjectsZooKeeperStorage` uses the following components:

- `ZooKeeperRetriesControl` with its `retryLoop()` method for retry management
- A `zookeeper_getter` member that can provide fresh ZooKeeper sessions
- `getObjectNamesAndSetWatch()` to fetch object names and register watches
- `tryLoadObject()` to load individual UDF objects from ZooKeeper
- `setAllObjects()` to update the stored objects
- `LOG_DEBUG` for debug logging
