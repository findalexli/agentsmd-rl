# Fix Session Cache Race Condition in Email/Password Login

## Problem

There's a race condition in the email/password login handler (`POST /v1/account/sessions/email`) that can cause newly created sessions to be immediately rejected as invalid.

When a user logs in with email/password:
1. The current code purges the user cache from Redis **before** creating the session document
2. This opens a window where concurrent requests (from different Swoole workers sharing the same Redis cache) can re-cache a stale user document without the new session
3. Subsequent requests using the new session then fail with 401 errors because the cached user document doesn't contain the session

## Symptoms

- User successfully logs in (receives session cookie)
- Immediate subsequent requests using that session return 401 Unauthorized
- The issue is timing-dependent and more likely under concurrent load

## Your Task

1. **Locate the bug**: Find the email/password login handler in `app/controllers/api/account.php`. Look around line 1106 where sessions are created.

2. **Identify the issue**: Look for the sequence where `purgeCachedDocument('users', ...)` and `createDocument('sessions', ...)` are called. The current order creates the race window.

3. **Apply the fix**: Reorder these operations so that:
   - The session document is created **first**
   - The user cache is purged **after** the session exists

4. **Verify**: Ensure the fix follows the same pattern already used by:
   - Anonymous sessions (around line 1269)
   - Token-based flows (magic URL, OTP, phone)
   - OAuth flows

## Constraints

- Only modify the order of the two operations (purge and create)
- Do not change any other logic, variable names, or formatting
- The fix must maintain the exact same indentation and code style

## Files to Modify

- `app/controllers/api/account.php` - The email/password login handler

Look for the code handling `POST /v1/account/sessions/email` and find where the session is created and the user cache is purged.
