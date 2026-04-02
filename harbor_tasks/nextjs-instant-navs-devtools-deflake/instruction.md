# Flaky test: `instant-navs-devtools` timing out on element selector

The integration test at `test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts` is flaking intermittently. The `clickStartClientNav` helper function uses `elementByCssInstant` to locate the `[data-instant-nav-client]` button, but this is racing with Playwright's IPC communication, causing sporadic timeouts.

The `*instant` selector variants (like `elementByCssInstant`) use a very short internal timeout that doesn't account for IPC latency. While most `*instant` selectors in the test work fine (e.g., for the panel itself), the one in `clickStartClientNav` is particularly sensitive because it follows a series of UI transitions.

## What to fix

The `clickStartClientNav` function in the test file needs to be made more resilient to timing issues. The element lookup for `[data-instant-nav-client]` should not race Playwright's IPC but should still resolve quickly (this element should already be present in the DOM, so a long timeout is not appropriate).

## Files involved

- `test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts` — the test file containing the flaky helper
