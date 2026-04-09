# Edge browser crashes when closing context with ongoing downloads

## Problem

When using Microsoft Edge (Chromium-based), closing a browser context while downloads are still in progress causes crashes. The `Download` class currently handles cancellation only through the `Artifact` callback, but there is no way to cancel downloads directly from outside the download object. This means the browser context disposal proceeds without cancelling active downloads first, leading to crashes specific to Edge.

## Expected Behavior

When a browser context is closed, any ongoing downloads should be cancelled before the context is actually disposed. The `Download` class should expose a way to cancel itself, and the Chromium browser context should use this to cancel all active downloads before sending the `disposeBrowserContext` command.

## Files to Look At

- `packages/playwright-core/src/server/download.ts` — the `Download` class that manages individual file downloads
- `packages/playwright-core/src/server/chromium/crBrowser.ts` — `CRBrowserContext` which handles context lifecycle including closure
