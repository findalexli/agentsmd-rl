# Fix Stale ZooKeeper Session Crash in UDF Retry Loop

## Problem

The `refreshObjects` function in `UserDefinedSQLObjectsZooKeeperStorage` crashes when handling transient ZooKeeper/Keeper errors. The issue is in the session management during the retry loop.

When the function encounters a Keeper error and triggers a retry via `ZooKeeperRetriesControl`, it continues using the original `zookeeper` session handle that was passed as a parameter. This session may have expired during the error, leading to:
- Watches being set on a dead session
- Subsequent operations failing with stale session errors
- Potential crashes due to invalid session state

## What You Need to Fix

In `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`, modify the `refreshObjects` function to:

1. **Move `object_names` fetching inside the retry loop** - Currently `Strings object_names = getObjectNamesAndSetWatch(...)` happens BEFORE the `retryLoop`. It should be inside the lambda so it's re-fetched with a fresh session on each retry.

2. **Add session renewal logic** - Inside the `retryLoop` lambda, before fetching object names:
   - Check if this is a retry using `retries_ctl.isRetry()`
   - If so, obtain a fresh ZooKeeper session via `zookeeper_getter.getZooKeeper().first`
   - Store this in a local `current_zookeeper` variable

3. **Use the live session** - Update `getObjectNamesAndSetWatch` and `tryLoadObject` calls to use `current_zookeeper` instead of the stale `zookeeper` parameter.

4. **Update comments** - The current comment mentions "5-second sleep in processWatchQueue" which is misleading. Update it to explain that on retry we obtain a fresh session and re-fetch the object list so watches are set on the live session.

## Key Pointers

- Look for the `retryLoop` call and the lambda passed to it
- The `ZooKeeperRetriesControl` class has an `isRetry()` method
- The `zookeeper_getter` is a member variable that provides fresh sessions
- Keep the retry configuration constants (`max_retries`, `initial_backoff_ms`, `max_backoff_ms`)
- Follow Allman brace style (opening brace on new line) as required by ClickHouse CI

## Expected Behavior After Fix

When a transient Keeper error occurs during `refreshObjects`:
1. The retry loop catches the error
2. On retry, a fresh ZooKeeper session is obtained
3. Object names are re-fetched with the new session (setting watches on live session)
4. Objects are loaded using the current (valid) session
5. If retries are exhausted, the exception propagates (doesn't silently fail)

## Testing

The fix should:
- Compile without syntax errors
- Maintain the same retry configuration
- Properly renew sessions during retries
- Not use sleep calls for race conditions (this is explicitly forbidden)
