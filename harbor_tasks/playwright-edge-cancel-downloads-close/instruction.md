# Edge browser crashes when closing context with ongoing downloads

## Problem

When using Microsoft Edge (Chromium-based), closing a browser context while downloads are still in progress causes crashes. The `Download` class currently handles cancellation only through the `Artifact` callback, but there is no way to cancel downloads directly from outside the download object. This means the browser context disposal proceeds without cancelling active downloads first, leading to crashes specific to Edge.

## Expected Behavior

1. **Add a `cancel()` method to the `Download` class.** The browser context already exposes a `cancelDownload(uuid)` method that cancels a download given its UUID. The new `cancel()` method should delegate to this by accessing the page's browser context and calling `cancelDownload` with the download's UUID. The UUID must be accessed as a stored instance field (via `this.<field>`) rather than as a closure-captured constructor parameter.

2. **Use public naming for the cancel method.** Per the project's `CLAUDE.md` (lines 99-102), methods that are used in other files must use public naming — no underscore prefix. Since `cancel()` will be called from `crBrowser.ts`, it must be `cancel()` not `_cancel()`.

3. **Cancel all downloads before context disposal.** In `CRBrowserContext`, before sending the `Target.disposeBrowserContext` command, iterate over the context's `_downloads` collection (a `Set` of `Download` instances that each download registers itself in during construction) and call `cancel()` on each one.

## Files to Look At

- `packages/playwright-core/src/server/download.ts` — the `Download` class that manages individual file downloads
- `packages/playwright-core/src/server/chromium/crBrowser.ts` — `CRBrowserContext` which handles context lifecycle including closure
