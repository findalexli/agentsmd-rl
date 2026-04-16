# Fix stale ZooKeeper session in UDF retry loop

## Problem

In `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`, the `refreshObjects()` method has a bug that causes crashes when ZooKeeper sessions expire during retry attempts.

### Symptom

The `refreshObjects()` method captures the ZooKeeper session handle and object names before entering the retry loop. When a transient Keeper error triggers a retry, the code uses the captured (now expired) session and stale object names, causing crashes or incorrect behavior.

## Code under test

The `refreshObjects()` method in `UserDefinedSQLObjectsZooKeeperStorage.cpp` uses:
- `ZooKeeperRetriesControl` with `retryLoop()` for retry management
- `zookeeper_getter.getZooKeeper()` to obtain ZooKeeper sessions
- `getObjectNamesAndSetWatch()` to fetch object names and register watches
- `tryLoadObject()` to load individual UDF objects
- `setAllObjects()` to update stored objects
- `retries_ctl.isRetry()` to detect retry attempts
