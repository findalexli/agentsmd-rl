# Flaky prefetch test: element assertion fails intermittently after navigation

## Problem

The e2e test `should not unintentionally modify the requested prefetch by escaping the uri encoded query params` in `test/e2e/app-dir/app-prefetch/prefetching.test.ts` is flaky.

After clicking the `#prefetch-via-link` element, the test immediately asserts that `#accordion-to-dashboard` exists on the homepage. This assertion sometimes fails because the element is not yet rendered — the page transition hasn't fully completed by the time the assertion runs.

## Context

The test navigates from a prefetch test page back to the homepage by clicking a link, then checks for the presence of a DOM element. After a recent Playwright upgrade, timing has shifted slightly and the assertion occasionally runs before the element is in the DOM.

## Files

- `test/e2e/app-dir/app-prefetch/prefetching.test.ts` — the flaky test (look at the test around the `#accordion-to-dashboard` assertion after the link click)

## Expected behavior

The test should reliably wait for the element to appear after navigation before asserting, rather than assuming it's immediately available. Check the project's testing conventions for the idiomatic way to handle this kind of timing issue.
