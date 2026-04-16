# bun-webview-test-async-fix

## Problem Statement

The Bun WebView test suite has multiple issues causing CI failures on macOS.

### Issue 1: Async rejection handling in webview-chrome.test.ts

A test that verifies `click()` rejects on invalid selector syntax uses a buggy async pattern. The double-await causes the rejection to fire before `expect()` can intercept it, resulting in an unhandled promise rejection rather than a clean assertion failure.

### Issue 2: rAF-dependent tests hang on macOS CI

Tests using `click(selector)` and `scrollTo(selector)` poll for actionability by waiting on `requestAnimationFrame`. On macOS CI, the headless `WKWebView` has no display attached, so rAF never fires and these tests hang.

The existing code uses inconsistent patterns for conditional test skipping:
- `test.todoIf(isCI)` in some places
- `it.todoIf(isCI)` in others (becomes `test.skip.todoIf()` on non-macOS, throwing at file load time)
- Plain `it(...)` in others

The rAF-dependent tests that need consistent skipping are:
- `click(selector) waits for actionability, clicks center`
- `click(selector) waits for element to appear`
- `click(selector) waits for element to stop animating`
- `click(selector) rejects on timeout when obscured`
- `click(selector) with options`
- `scroll dispatches native wheel event with isTrusted`
- `scroll: sequential calls in same view`
- `scroll: horizontal`
- `scroll: interleaved with click in same view`
- `scroll: survives navigate (fresh scrolling tree)`
- `scroll: targets inner scrollable under view center`
- `scrollTo(selector) waits for element to appear`
- `scrollTo(selector) rejects on timeout`
- `document.visibilityState is visible and rAF fires`

### Issue 3: Platform version compatibility

The localStorage persistence test relies on functionality available only in macOS 15.2+ (specifically `_WKWebsiteDataStoreConfiguration initWithDirectory:`). The test name is:
- `persistent dataStore: localStorage survives across instances`

### Issue 4: WebView.closeAll() test encoding and stderr

The `WebView.closeAll()` test uses raw HTML in a data URL without proper encoding and uses `stderr: 'pipe'` unnecessarily.

## Files to Investigate

- `test/js/bun/webview/webview-chrome.test.ts` - Contains the async rejection handling issue
- `test/js/bun/webview/webview.test.ts` - Contains rAF-dependent tests and conditional skipping patterns

## Harness Utilities Available

The harness module provides these utilities for platform detection:
- `isMacOS` - boolean, true when running on macOS
- `isCI` - boolean, true when running in CI environment
- `isMacOSVersionAtLeast(version: number)` - function returning true if macOS version >= specified

## Expected Behavior

1. The buggy double-await async pattern must not exist in webview-chrome.test.ts. The `rejects.toThrow()` must properly intercept rejection, not cause unhandled promise rejection.

2. The test that uses `":::invalid"` as selector must have the correct async pattern for promise rejection testing.

3. The `isMacOSVersionAtLeast` function must be imported from harness in webview.test.ts.

4. A helper must be defined in webview.test.ts that conditionally skips rAF-dependent tests on macOS CI (where rAF doesn't fire in headless WKWebView).

5. All rAF-dependent tests listed above must use a helper (not direct `it()` calls) for conditional skipping.

6. A helper must be defined in webview.test.ts that conditionally runs persistent dataStore tests only on macOS 15.2+.

7. The `persistent dataStore: localStorage survives across instances` test must use a helper for platform version checking.

8. No direct `test.todoIf(isCI)` calls should remain outside helper definitions.

9. The `WebView.closeAll()` test must properly encode HTML in data URLs.

10. The `WebView.closeAll()` test should not use `stderr: 'pipe'`.

## Quality Requirements

- Modified test files must have valid TypeScript syntax
- Files must pass prettier format checks
- Files must have valid Node.js syntax
- `isMacOSVersionAtLeast` must be imported from harness