# bun-webview-test-async-fix

## Problem Statement

The Bun WebView test suite has multiple issues causing CI failures on macOS.

### Issue 1: Async rejection handling

A test verifying that `click()` rejects on invalid selector syntax is not catching the rejection properly. The rejection fires before the test framework can intercept it, causing an unhandled promise rejection instead of a clean assertion failure.

### Issue 2: rAF-dependent tests hang on macOS CI

Tests using `click(selector)` and `scrollTo(selector)` poll for actionability by waiting on `requestAnimationFrame`. On macOS CI, the headless `WKWebView` has no display attached, so rAF never fires and these tests hang.

Existing code uses inconsistent patterns for conditional test skipping:
- `test.todoIf(isCI)` in some places
- `it.todoIf(isCI)` in others (becomes `test.skip.todoIf()` on non-macOS, throwing at file load time)
- Plain `it(...)` in others

### Issue 3: Platform version compatibility

The localStorage persistence test relies on functionality available only in macOS 15.2+ (specifically `_WKWebsiteDataStoreConfiguration initWithDirectory:`). Tests requiring this version check are not properly guarded.

### Issue 4: WebView.closeAll() test issues

The `WebView.closeAll()` test uses raw HTML in a data URL without proper encoding and uses `stderr: 'pipe'` unnecessarily.

## Expected Behavior

1. Rejection tests should properly catch rejections so the test framework's `.rejects.toThrow()` works correctly.

2. All rAF-dependent tests should be conditionally skipped on macOS CI (where rAF doesn't fire) and on non-macOS platforms (where WebView only works on macOS).

3. Tests requiring specific macOS versions should use appropriate version guards via `isMacOSVersionAtLeast` from harness.

4. The `WebView.closeAll()` test should properly encode HTML in data URLs and avoid unnecessary stderr configuration.

## Files to Investigate

- `test/js/bun/webview/webview-chrome.test.ts` - Contains the async rejection handling issue
- `test/js/bun/webview/webview.test.ts` - Contains rAF-dependent tests and conditional skipping patterns

## Guidance

- Harness provides `isMacOS`, `isCI`, and `isMacOSVersionAtLeast` for platform detection
- A helper similar to `const it = isMacOS ? test : test.skip;` could consolidate CI-skipping logic for rendering-dependent tests
- Tests for `document.visibilityState`, `click(selector)`, `scrollTo(selector)`, and `scroll` operations depend on animation frames firing
- The localStorage persistence test has platform version requirements
- Data URLs containing HTML should use proper encoding
