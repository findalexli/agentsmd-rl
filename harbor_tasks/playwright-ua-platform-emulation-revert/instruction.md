# Revert cross-browser navigator.platform override from user agent emulation

## Problem

A recently-merged change added logic to sync `navigator.platform` with a custom user agent string across all browsers (Chromium, Firefox, WebKit). This shared `calculateUserAgentEmulation` function in `browserContext.ts` parses the user agent to derive both `navigatorPlatform` and `userAgentMetadata`, and each browser driver uses it to override `navigator.platform` accordingly.

This cross-browser platform override is causing regressions — `navigator.platform` should NOT be overridden in Firefox and WebKit when a custom user agent is set. The platform override should be reverted from these browsers. Chromium still needs its UA client hints metadata (the `userAgentMetadata` sent via CDP), but the `navigator.platform` override via the `platform` parameter should also be removed there.

## Expected Behavior

- Setting a custom user agent should **not** change `navigator.platform` in any browser
- Chromium should still send `userAgentMetadata` to the CDP `Emulation.setUserAgentOverride` command (for `sec-ch-ua-*` headers and `navigator.userAgentData`), but should NOT send the `platform` parameter
- Firefox should not call any platform override protocol command when setting user agent
- WebKit should not call any platform override protocol command when setting user agent
- The shared `calculateUserAgentEmulation` function can be removed or refactored — it was only needed for the platform syncing feature

## Files to Look At

- `packages/playwright-core/src/server/browserContext.ts` — shared browser context utilities, contains the `calculateUserAgentEmulation` function
- `packages/playwright-core/src/server/chromium/crPage.ts` — Chromium page implementation, calls `calculateUserAgentEmulation` in `_updateUserAgent`
- `packages/playwright-core/src/server/firefox/ffBrowser.ts` — Firefox browser context, calls `setPlatformOverride` based on parsed user agent
- `packages/playwright-core/src/server/webkit/wkPage.ts` — WebKit page implementation, calls `overridePlatform` in `updateUserAgent`
