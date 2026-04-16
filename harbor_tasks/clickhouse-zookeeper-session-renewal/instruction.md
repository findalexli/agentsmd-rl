# Fix Stale ZooKeeper Session Crash in UDF Retry Loop

## Problem

The `refreshObjects` function in `UserDefinedSQLObjectsZooKeeperStorage` crashes when handling transient ZooKeeper/Keeper errors during the retry loop.

When the function encounters a Keeper error and triggers a retry, it continues using the original ZooKeeper session handle that was passed as a function parameter. This session may have expired during the error. The problem is:

- Watches are set on a potentially dead session
- Subsequent operations fail with stale session errors
- The crash manifests as invalid session state during retries

The stale session causes the function to crash or behave incorrectly when transient Keeper errors occur.

## Expected Behavior After Fix

When a transient Keeper error occurs during `refreshObjects`:

1. The retry loop catches the error
2. On retry, a fresh ZooKeeper session must be obtained (the provided handle may point to an expired session)
3. Object names must be re-fetched with the new session (watches set on live session)
4. Objects must be loaded using the current (valid) session
5. If retries are exhausted, the exception must propagate (not silently fail)

## Required Implementation

The fix must ensure:

1. **Session renewal on retry**: The retry loop must detect when a retry is occurring and obtain a fresh session
2. **Fresh session variable**: A local variable must hold the active session (initialized from the parameter, renewed on retry)
3. **Object names in retry loop**: The object name fetching must be inside the retry loop so it re-fetches on each retry
4. **Use current session**: All operations inside the retry loop must use the current (potentially renewed) session
5. **Updated comments**: Comments must explain that the session is renewed on retry and that the object list is re-fetched
6. **Remove misleading comment**: Any comment referencing "5-second sleep in processWatchQueue" must be removed

## Style Requirements

- Follow Allman brace style (opening brace on new line)
- No sleep calls for race conditions (explicitly forbidden)
- Keep existing retry configuration constants