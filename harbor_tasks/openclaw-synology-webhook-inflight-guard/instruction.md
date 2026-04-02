# Synology Chat webhook handler lacks pre-auth concurrency limit

## Problem

The Synology Chat webhook handler in `extensions/synology-chat/src/webhook-handler.ts` has rate limiting and invalid-token throttling, but there is no guard against a flood of concurrent requests that are still in the pre-auth body-reading phase. An attacker (or a misconfigured upstream) can open many simultaneous connections that stall during body parsing, exhausting server resources before any authentication or rate-limit check fires.

Other webhook handlers in the codebase already use a shared in-flight limiter from `openclaw/plugin-sdk/webhook-ingress` to cap how many requests can be in the pre-auth pipeline at the same time, keyed per logical endpoint. The Synology Chat handler does not use this mechanism.

## Expected behavior

When the number of concurrent pre-auth requests (body reads in progress) from the same logical source exceeds the limiter's threshold, excess requests should be rejected immediately with HTTP 429 before any body parsing begins. Requests that are already past the pre-auth phase (e.g., delivering a reply asynchronously) should not be affected.

## Relevant files

- `extensions/synology-chat/src/webhook-handler.ts` — the `createWebhookHandler` function and its entry-point handler
- `openclaw/plugin-sdk/webhook-ingress` — shared utilities including in-flight limiting
- `extensions/synology-chat/src/test-http-utils.ts` — test helpers for mock HTTP requests/responses
- `extensions/synology-chat/src/webhook-handler.test.ts` — existing test suite

## Hints

- Look at how `beginWebhookRequestPipelineOrReject` and `createWebhookInFlightLimiter` are used by other webhook handlers in the repo.
- The in-flight guard should be scoped to a key that makes sense for the Synology Chat handler (consider what identifies a logical endpoint).
- The guard's lifecycle should only span the pre-auth request pipeline, not the async reply delivery that follows.
- The test helper's `makeRes()` may need updating to support how the guard writes status codes.
