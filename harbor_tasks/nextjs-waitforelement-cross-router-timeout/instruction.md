# Bug: Flaky cross-router navigation test times out intermittently in CI

## Context

The e2e test suite for App Router / Pages Router interoperability (`test/e2e/app-dir/interoperability-with-pages/navigation.test.ts`) is intermittently failing in CI. The tests navigate between pages served by the App Router and pages served by the Pages Router, which triggers a full-page reload each time (the two routers cannot share client-side navigation).

In development mode, the destination page is compiled on-demand the first time it is visited. In CI environments under load, this on-demand compilation consistently takes ~13 seconds. The test assertions that wait for the destination page element to appear are timing out before compilation finishes.

The failures are non-deterministic and load-sensitive — they pass locally but fail frequently in CI, especially the `app -> pages` direction.

## Reproduction

1. Run the interoperability navigation tests in a resource-constrained environment (or simulate slow compilation)
2. Observe that `waitForElementByCss` calls after cross-router navigation (click, back, forward) time out before the compiled page loads
3. The default wait timeout (~10 seconds) is insufficient for the ~13 second on-demand compilation

## Where to look

- `test/e2e/app-dir/interoperability-with-pages/navigation.test.ts` — all four test cases exercise cross-router navigation and use `waitForElementByCss` to wait for destination page elements

## Expected behavior

All `waitForElementByCss` calls that wait for an element after a cross-router navigation should use an explicit timeout large enough to accommodate on-demand compilation in CI (at least 20 seconds). The fix should include a brief comment explaining why the increased timeout is necessary.
