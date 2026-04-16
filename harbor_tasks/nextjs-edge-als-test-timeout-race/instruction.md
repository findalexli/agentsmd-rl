# Edge AsyncLocalStorage test timeout and race condition

The e2e test at `test/e2e/edge-async-local-storage/index.test.ts` is flaky in deploy mode. When running in deploy mode, the deployment step can exceed the 60-second per-test timeout. Because `createNext` is called inside each `it.each` test body, the test times out before the Next.js instance is assigned to the local variable. This causes:

1. The `afterEach` cleanup hook tries to call `.destroy()` on an unassigned variable, throwing a `TypeError`.
2. The module-level instance reference is left pointing at the stale, half-initialized deploy instance.
3. The next test case detects the leftover instance and fails with `"createNext called without destroying previous instance"`.

Additionally, the API route handlers are currently defined as inline template strings inside the test file rather than in separate fixture files.

## Your task

Fix the test so that:
- Instance lifecycle management uses a longer setup timeout that isn't reset by the per-test timeout
- API route handlers are served from external fixture files rather than inline template strings
- The race condition between instance creation and cleanup is eliminated

The fix must preserve all existing test behavior: `fetchViaHTTP` from `next-test-utils` must still be used, concurrent requests must still be sent with `req-id` headers via `Promise.all`, and the test must still verify edge runtime behavior.

## Expected behavior

After fixing, two API route handlers must exist that produce the following JSON responses:

1. **Single AsyncLocalStorage instance**: when called with a request whose `req-id` header is `<id>`, the response must be:
   ```json
   {"id": "<id>"}
   ```

2. **Nested AsyncLocalStorage instances**: when called with a request whose `req-id` header is `<id>`, the response must be:
   ```json
   {"id": "<id>", "nestedId": "nested-<id>"}
   ```

Both handlers must run on the edge runtime and use `Response.json()` to return JSON.

The test must not call `createNext` inside an `it` or `test` callback body.

## Relevant files

- `test/e2e/edge-async-local-storage/index.test.ts` — the flaky test
- Route handler fixture files must be alongside the test in the same directory