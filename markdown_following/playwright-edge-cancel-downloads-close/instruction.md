# Edge browser crashes when closing context with ongoing downloads

## Problem

When using Microsoft Edge (Chromium-based), closing a browser context while downloads are still in progress causes crashes. The `Download` class currently handles cancellation only through the `Artifact` callback, but there is no way to cancel downloads directly from outside the download object. This means the browser context disposal proceeds without cancelling active downloads first, leading to crashes specific to Edge.

## Expected Behavior

1. **The `Download` class should expose a way to cancel an ongoing download programmatically.** The browser context already exposes a `cancelDownload(uuid)` method that cancels a download given its UUID. The `Download` class should provide a public method (no underscore prefix, as it will be called from other files per the project's `CLAUDE.md` conventions) that cancels the download by delegating to this browser context method, using a stored instance field (not a closure-captured constructor argument).

2. **Before disposing the browser context, all ongoing downloads should be cancelled.** In `CRBrowserContext`, before the context is fully disposed via `Target.disposeBrowserContext`, any active downloads associated with that context must be cancelled first to prevent Edge-specific crashes. The cancellation should iterate through all tracked downloads and attempt to cancel each one.

## Files to Look At

- `packages/playwright-core/src/server/download.ts` — the `Download` class that manages individual file downloads
- `packages/playwright-core/src/server/chromium/crBrowser.ts` — `CRBrowserContext` which handles context lifecycle including closure
