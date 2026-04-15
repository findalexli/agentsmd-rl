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
2. On retry, a fresh ZooKeeper session must be obtained
3. Object names must be re-fetched with the new session (watches set on live session)
4. Objects must be loaded using the current (valid) session
5. If retries are exhausted, the exception must propagate (not silently fail)

## Required Implementation

The fix must include these specific patterns:

1. **Session renewal check**: The code must check `retries_ctl.isRetry()` to detect when a retry is occurring
2. **Fresh session acquisition**: On retry, obtain a fresh session via `zookeeper_getter.getZooKeeper().first`
3. **Variable naming**: Use a `current_zookeeper` variable to hold the active session (initialized from the parameter, renewed on retry)
4. **Move object_names into loop**: The `Strings object_names = getObjectNamesAndSetWatch(...)` declaration must be inside the retryLoop lambda so it re-fetches on each retry
5. **Use current_zookeeper**: All calls to `getObjectNamesAndSetWatch` and `tryLoadObject` must use `current_zookeeper`, not the stale parameter
6. **Comment updates**: Include comments with the following phrases:
   - "Renew the session on retry"
   - "re-fetch the object list"
   - "watches are set on the live session"
7. **Remove old comment**: Remove the comment mentioning "5-second sleep in processWatchQueue"

## Style Requirements

- Follow Allman brace style (opening brace on new line)
- No sleep calls for race conditions (explicitly forbidden)
- Keep existing retry configuration constants
