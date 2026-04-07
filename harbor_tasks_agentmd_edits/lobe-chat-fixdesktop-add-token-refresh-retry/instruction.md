# Desktop OIDC token refresh logs users out on transient network errors

## Problem

Desktop users connecting to a remote OIDC server are frequently logged out whenever a token refresh request fails for any reason — including temporary network glitches, brief server unavailability, or other transient errors. The current implementation clears all tokens and forces re-authorization on every refresh failure, regardless of whether the error is recoverable.

There is also a secondary issue: when `rotateRefreshToken` is enabled and the old refresh token is consumed, any interruption (network issue, crash) between consuming the old token and saving the new one makes the session unrecoverable.

## Expected Behavior

Transient network errors during token refresh should be retried automatically (with exponential backoff) before giving up. Only permanent, non-retryable errors (e.g., `invalid_grant`, `access_denied`) should trigger token clearing and re-authorization. Consumed refresh tokens should be reusable within a short grace period to survive client-side interruptions.

Additionally, the project's CLAUDE.md workflow instructions should be reviewed and updated to reflect the correct issue management process — issues should be set to "In Review" when a PR is created, not "Done".

## Files to Look At

- `apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts` — handles the OIDC token refresh logic; needs retry mechanism and error classification
- `apps/desktop/src/main/controllers/AuthCtr.ts` — orchestrates auto-refresh and token lifecycle; needs to distinguish retryable vs permanent errors before clearing tokens
- `src/libs/oidc-provider/adapter.ts` — OIDC adapter for token storage; needs grace period for consumed refresh tokens
- `apps/desktop/package.json` — may need the `async-retry` dependency for backoff logic
- `CLAUDE.md` — project workflow instructions; verify the Linear issue status workflow is accurate
