# Fix Stale ZooKeeper Session in UDF Retry Loop

## Problem

The `refreshObjects` function in `UserDefinedSQLObjectsZooKeeperStorage` has a bug where it uses a stale ZooKeeper session handle during retries.

When the function encounters a transient Keeper error and the retry loop triggers another attempt, it continues using the original ZooKeeper session that was passed as a function parameter. This session may have expired during the error. The symptom is:

- Watches are set on a potentially dead session
- Subsequent operations fail with stale session errors
- The error manifests as invalid session state during retries

## Expected Behavior After Fix

When a transient Keeper error occurs during `refreshObjects`:

1. The retry loop catches the error
2. On each retry attempt, the code must obtain a fresh ZooKeeper session (the provided handle may be expired)
3. Object names must be re-fetched with the new session (watches set on live session)
4. Objects must be loaded using the current (valid) session
5. If retries are exhausted, the exception must propagate (not silently fail)

## Requirements

The fix must ensure:

1. **Session renewal on retry**: The retry loop must detect when a retry is occurring and obtain a fresh session using the `zookeeper_getter` member
2. **Local session variable**: A local variable must track the active session (initialized from the parameter, renewed on retry)
3. **Object names inside retry loop**: The object name fetching must be inside the retry loop so it re-fetches on each retry
4. **Use active session**: All operations inside the retry loop must use the active (potentially renewed) session
5. **Updated comments**: Comments must explain that the session is renewed on retry and that the object list is re-fetched
6. **Remove misleading comment**: Any comment referencing "5-second sleep in processWatchQueue" must be removed

## Style Requirements

- Follow Allman brace style (opening brace on new line)
- No sleep calls for race conditions (explicitly forbidden)
- Keep existing retry configuration constants
