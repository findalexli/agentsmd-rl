# webview: skip rendering-dependent tests on macOS CI

## Problem

The Bun WebView test suite has multiple issues causing CI failures:

1. **Async/await bug in webview-chrome.test.ts**: A test checking that `click(selector)` rejects on invalid selector syntax has a stray inner `await` that causes the rejection to throw before the test framework can catch it. The test at line ~668 has:
   ```typescript
   await expect(await view.click(":::invalid")).rejects.toThrow();
   ```
   This pattern causes the promise rejection to happen before `.rejects.toThrow()` can intercept it.

2. **rAF-dependent tests hang on macOS CI**: Tests using `click(selector)` and `scrollTo(selector)` poll for actionability by waiting on `requestAnimationFrame` between checks. On macOS CI, the headless `WKWebView` gets no `CVDisplayLink` callbacks (no display attached), so rAF never fires and these tests hang until timeout.

3. **Inconsistent test skipping patterns**: There are multiple inconsistent patterns for conditionally skipping tests on macOS CI:
   - `(isMacOS ? test.todoIf(isCI) : test.skip)("test name", ...)`
   - `it.todoIf(isCI)("test name", ...)`
   - `it("test name", ...)` for tests that should be conditional

   The second pattern (`it.todoIf(isCI)`) is particularly problematic because it becomes `test.skip.todoIf()` on non-macOS platforms, which throws at file load time.

4. **Missing version check for persistent dataStore tests**: The `localStorage` persistence test requires macOS 15.2+ (`_WKWebsiteDataStoreConfiguration initWithDirectory:`), but this version check is missing.

5. **Minor issues in WebView.closeAll() test**: The test uses raw HTML in a data URL without encoding, and unnecessarily captures stderr.

## Expected Behavior

1. The `click(selector)` rejection test should properly catch the rejection using `await expect(view.click(...)).rejects.toThrow()` (without the inner await).

2. All rAF-dependent tests should use a consistent `itRendering` helper that:
   - On macOS: uses `test.todoIf(isCI)` to skip on CI (where rAF doesn't fire)
   - On non-macOS: uses `test.skip` since WebView only works on macOS

3. The `itRendering` helper should be applied to all tests that depend on rendering/animation:
   - `document.visibilityState is visible and rAF fires`
   - `click(selector) waits for actionability, clicks center`
   - `click(selector) waits for element to appear`
   - `click(selector) waits for element to stop animating`
   - `click(selector) rejects on timeout when obscured`
   - `click(selector) with options`
   - `scrollTo(selector) waits for element to appear`
   - `scrollTo(selector) rejects on timeout`
   - `scroll dispatches native wheel event with isTrusted`
   - `scroll: sequential calls in same view`
   - `scroll: horizontal`
   - `scroll: interleaved with click in same view`
   - `scroll: survives navigate (fresh scrolling tree)`
   - `scroll: targets inner scrollable under view center`

4. A new `itPersistentDataStore` helper should be defined for macOS 15.2+ only tests.

5. The `isMacOSVersionAtLeast` utility should be imported from `harness`.

## Files to Look At

- `test/js/bun/webview/webview-chrome.test.ts` - Contains the async/await bug in the Chrome WebView tests
- `test/js/bun/webview/webview.test.ts` - Contains the rAF-dependent tests and inconsistent skipping patterns

## Hints

- Look for the pattern `await expect(await view.click` - this is the bug
- Look for tests using `isCI` checks with rendering-dependent operations
- The `isMacOSVersionAtLeast` function is available in the `harness` module
- The fix should consolidate all rendering-dependent tests under a single helper
