# Flaky typed-routes tests timing out on CI

## Bug Description

Three tests in `test/e2e/app-dir/typed-routes/typed-routes.test.ts` are intermittently failing on CI with `Failed to retry within 3000ms`:

- `typed-routes > should generate route types correctly`
- `typed-routes > should have passing tsc after start`
- `typed-routes > should correctly convert custom route patterns from path-to-regexp to bracket syntax`

## Root Cause

The Next.js dev server logs `✓ Ready in X` to stdout before the full initialization sequence completes. Specifically, route type generation (`routes.d.ts`) happens inside `setupDevBundler()`'s Watchpack `aggregated` event handler, which runs *after* `getRequestHandlers()` resolves and the "Ready" message is emitted.

On loaded CI runners, the gap between the "Ready" log and the completion of `routes.d.ts` generation can exceed the default `retry()` timeout of 3000ms, causing the tests to time out before the file exists.

There is a secondary issue in the `should have passing tsc after start` test: it calls `next.stop()` immediately after the server is considered ready, before `routes.d.ts` has been written. This means `tsc` runs against a project missing the generated types, causing type errors.

## Relevant Files

- `test/e2e/app-dir/typed-routes/typed-routes.test.ts` — the failing test file
- `packages/next/src/server/lib/start-server.ts` — where the "Ready" message is logged before full initialization

## Expected Behavior

All three tests should pass reliably on CI, even when the server takes longer than 3 seconds to complete route type generation after reporting readiness.
