# CLI Daemon: Honor PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD Environment Variable

## Problem

The CLI daemon currently does not respect the `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` environment variable. When this environment variable is set, browser installation should be skipped on daemon startup, but currently the daemon proceeds to check and install browsers regardless.

Additionally, the browser installation logic in `ensureConfiguredBrowserInstalled()` and `findOrInstallDefaultBrowser()` is repetitive and manually checks for executable existence before installing. This logic should be refactored to use the `resolveBrowsers()` helper which properly handles browser dependencies (like ffmpeg).

## Expected Behavior

1. When `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` environment variable is set (to any truthy value), the daemon should skip browser installation entirely in `ensureConfiguredBrowserInstalled()`.

2. The browser installation logic should be refactored to:
   - Extract a `resolveAndInstall()` helper that uses `resolveBrowsers()` to resolve browsers and their dependencies
   - Use this helper in both `ensureConfiguredBrowserInstalled()` and `findOrInstallDefaultBrowser()`
   - Ensure ffmpeg is properly resolved and installed as a dependency when a browser is found

## Files to Look At

- `packages/playwright-core/src/tools/cli-daemon/program.ts` — The CLI daemon program that handles browser installation on startup. Look at `ensureConfiguredBrowserInstalled()` and `findOrInstallDefaultBrowser()` functions.

## Implementation Notes

The `getAsBooleanFromENV()` utility is available from `../../server/utils/env` for checking environment variables. The `resolveBrowsers()` method on `browserRegistry` can resolve browsers with their dependencies by passing `{ shell: 'no' }` option.
