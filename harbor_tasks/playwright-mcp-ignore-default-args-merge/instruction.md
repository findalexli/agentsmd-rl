# fix(mcp): merge user ignoreDefaultArgs with persistent mode defaults

## Problem

When using Playwright's MCP persistent browser mode, any user-configured `ignoreDefaultArgs` in the browser launch options are silently ignored. Users who set `ignoreDefaultArgs` in their config (e.g., to remove `--password-store=basic` or `--force-color-profile=srgb` from Chromium's default arguments) find that their configuration has no effect — only `--disable-extensions` is ever removed.

## Expected Behavior

User-provided `ignoreDefaultArgs` should be respected and merged with the persistent mode's built-in `--disable-extensions` exclusion. When a user sets `ignoreDefaultArgs: true` (ignore all defaults), that should pass through unchanged.

## Files to Look At

- `packages/playwright-core/src/tools/mcp/browserFactory.ts` — the `createPersistentBrowser` function constructs launch options for persistent browser contexts
