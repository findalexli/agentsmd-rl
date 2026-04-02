# Bug: Dev server client fixture crashes on transient fetch failures and missing headers

## Context

The Bun dev server ("bake") test suite uses a Node.js-based client fixture (`test/bake/client-fixture.mjs`) that simulates a browser loading pages via `happy-dom`. The test harness (`test/bake/bake-harness.ts`) spawns this client as a subprocess.

## Problem

The client fixture has several error handling gaps that cause intermittent crashes and flaky tests:

1. **`loadPage()` has no retry logic**: When the dev server port isn't fully ready, `fetch()` throws a connection error and the process crashes with an unhandled rejection. There is no retry mechanism for transient network failures.

2. **Null content-type header causes TypeError**: In `loadPage()`, the code calls `.match()` directly on the result of `response.headers.get("content-type")` without checking if the header exists. When the content-type header is absent, this throws `TypeError: Cannot read properties of null (reading 'match')`.

3. **No `unhandledRejection` handler**: The process has no global handler for unhandled promise rejections, so any async error silently kills the client subprocess without useful diagnostics.

4. **Initial page load is not wrapped in try/catch**: The top-level `await loadPage()` call has no error handling, so any exception during the initial load results in an unhandled error.

5. **Client exit code not propagated**: When the client subprocess exits, its exit code is not forwarded to the `OutputLineStream` in the harness (`test/bake/bake-harness.ts`), making it harder to diagnose failures.

## Relevant Files

- `test/bake/client-fixture.mjs` — The client fixture script (main file to fix)
- `test/bake/bake-harness.ts` — The test harness `Client` class constructor (~line 817)

## Expected Behavior

- `loadPage()` should retry fetch on transient connection errors (with backoff)
- Null/missing content-type headers should be handled gracefully
- Unhandled promise rejections should be caught and reported with a meaningful exit code
- The initial page load should be wrapped in error handling
- The client process exit code should be forwarded to `OutputLineStream`
