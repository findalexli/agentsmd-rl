# Flaky URL Hash Client Navigation Tests

## Problem

The test suite at `test/development/pages-dir/client-navigation/url-hash.test.ts` has multiple flaky tests in the "Client navigation with URL hash" describe block.

The tests interact with browser elements (clicking links, reading text content, checking scroll positions) but immediately assert on DOM state right after triggering navigation or click events. Because browser actions like scrolling, hash changes, and DOM updates are asynchronous, these assertions sometimes run before the browser has finished updating, causing intermittent failures.

For example, a test might click a link and then immediately read `window.pageYOffset` or element text content, but the scroll or DOM update hasn't completed yet. This leads to flaky assertions that pass locally most of the time but fail intermittently in CI.

The affected test sections include:
- Hash change navigation (via `<Link>` and `<a>` tags)
- Scroll position assertions after hash navigation
- `asPath` verification after hash changes
- History state counter tests
- Back navigation hash change tests
- Empty hash navigation tests

## Relevant Files

- `test/development/pages-dir/client-navigation/url-hash.test.ts` — the flaky test file

## Expected Behavior

All tests in the url-hash test suite should pass reliably without intermittent failures by properly waiting for asynchronous browser state changes before making assertions.
