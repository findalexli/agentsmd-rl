# Synology Chat webhook handler lacks pre-auth concurrency limit

## Problem

The Synology Chat webhook handler has rate limiting and invalid-token throttling, but there is no guard against a flood of concurrent requests that are still in the pre-auth body-reading phase. An attacker (or a misconfigured upstream) can open many simultaneous connections that stall during body parsing, exhausting server resources before any authentication or rate-limit check fires.

Other webhook handlers in the codebase already use a shared in-flight limiter from `openclaw/plugin-sdk/webhook-ingress` to cap how many requests can be in the pre-auth pipeline at the same time. The Synology Chat handler does not use this mechanism.

## Expected behavior

When the number of concurrent pre-auth requests (body reads in progress) exceeds the limiter's threshold, excess requests should be rejected immediately with HTTP 429 before any body parsing begins. Requests that are already past the pre-auth phase (e.g., delivering a reply asynchronously) should not be affected.

## Implementation requirements

1. **Import from plugin-sdk**: Import the in-flight limiting utilities from `openclaw/plugin-sdk/webhook-ingress` (not from core internals like `src/plugin-sdk` or `plugin-sdk-internal`).

2. **Account-scoped in-flight key**: The pre-auth concurrency guard must be scoped per logical endpoint using the account's `accountId`. Do NOT use `remoteAddress` as the sole key—IP addresses can collapse behind proxies or become "unknown", making them unreliable for limiting.

3. **Guard placement**: The guard must be invoked at the start of request handling, before any authentication or body parsing, with early-return on rejection (HTTP 429).

4. **Guard lifecycle**: The guard's lifecycle must only span the pre-auth request pipeline (authentication and body reading). It must be released in a `try/finally` block (or equivalent) so that the async reply delivery phase that follows is not affected.

5. **Test helper update**: The `makeRes()` helper in `extensions/synology-chat/src/test-http-utils.ts` needs bidirectional synchronization between `statusCode` (property) and `_status` (internal storage) so that code setting `res.statusCode = 429` correctly updates `res._status` for test assertions.

6. **Test cleanup**: Provide a way for tests to reset the in-flight limiter state (e.g., a function named `clearSynologyWebhookRateLimiterStateForTest`).

## Files to modify

- `extensions/synology-chat/src/webhook-handler.ts` — the handler entry point
- `extensions/synology-chat/src/test-http-utils.ts` — the mock response helper
