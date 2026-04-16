# Fix Crash in UDF Retry Loop

## Problem

The `UserDefinedSQLObjectsZooKeeperStorage::refreshObjects` method crashes when a transient ZooKeeper/Keeper error triggers the retry loop. After a retry, the code may use a session handle that has expired, and ZooKeeper operations may reference stale data that was fetched before the retry occurred.

## Location

**File:** `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`
**Function:** `refreshObjects(const zkutil::ZooKeeperPtr & zookeeper, ...)`

## Bug Description

When a transient Keeper error causes the retry loop to execute again:
1. The session handle may be expired from the previous attempt
2. The object list was fetched before the retry loop started, so it reflects the old session's state on retry

## Expected Behavior

After a transient error, the retry loop should operate with a valid session and fresh data. All ZooKeeper operations inside the retry loop should use a session variable that is renewed on retry attempts. The object names should be fetched fresh inside the loop.

## What You Need to Know

The code uses:
- `ZooKeeperRetriesControl` with `retryLoop([&]{ ... })` lambda pattern
- `retries_ctl.isRetry()` method detects when the loop is running a retry attempt (not the first try)
- `zookeeper_getter.getZooKeeper().first` provides a fresh ZooKeeper session
- A local variable `current_zookeeper` should be used to hold the current session (initially assigned from the `zookeeper` parameter)
- `getObjectNamesAndSetWatch(zookeeper, object_type)` fetches object names and sets watches
- `tryLoadObject(zookeeper, ...)` loads individual objects

## Testing

Your fix will be verified by:
- Checking that `retries_ctl.isRetry()` is called to detect retry scenarios
- Verifying session renewal via `zookeeper_getter.getZooKeeper().first` when a retry is detected
- Confirming `Strings object_names` is declared and fetched inside the retry loop
- Ensuring `getObjectNamesAndSetWatch` and `tryLoadObject` use `current_zookeeper` (not the original `zookeeper` parameter)
- Validating session renewal occurs before object names are fetched inside the loop