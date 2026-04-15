# CLI Daemon: Honor PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD Environment Variable

## Problem

The CLI daemon in `packages/playwright-core/src/tools/cli-daemon/program.ts` has the following issues:

1. **Missing env var check**: The `ensureConfiguredBrowserInstalled()` function does not check the `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` environment variable. When this variable is set to a truthy value, the function should return early without performing any browser installation, but currently it always proceeds regardless.

2. **Fragile, duplicated installation logic**: Both `ensureConfiguredBrowserInstalled()` and `findOrInstallDefaultBrowser()` contain manually written browser installation code that checks for executable existence using `fs.existsSync` before calling `browserRegistry.install()`. This pattern does not resolve browser dependencies such as `ffmpeg`.

3. **Missing ffmpeg dependency**: When `findOrInstallDefaultBrowser()` finds an already-installed browser, it returns the channel name without ensuring that `ffmpeg` is also installed.

## Expected Behavior

1. At the very start of `ensureConfiguredBrowserInstalled()`, the `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` environment variable must be checked. The utility function `getAsBooleanFromENV` (importable from `../../server/utils/env`) should be used for this check. When the variable is truthy, the function must return immediately without any browser operations.

2. The manual `fs.existsSync` checks on executable paths should be removed from both functions. Browser installation should instead go through `browserRegistry.resolveBrowsers()` to resolve executables along with their dependencies, followed by `browserRegistry.install()`. The `{ shell: 'no' }` option should be passed to `resolveBrowsers()`.

3. The installation logic using `resolveBrowsers()` and `install()` should be factored into a shared async helper function that accepts a name or channel string parameter, to avoid duplication between the two call sites.

4. When `findOrInstallDefaultBrowser()` finds an installed browser channel, `ffmpeg` must also be resolved and installed before the function returns.

5. In the chromium fallback path of `findOrInstallDefaultBrowser()`, the old pattern `!fs.existsSync(chromiumExecutable?.executablePath()!)` must be removed. Chromium installation should go through the same consolidated approach.

## File

- `packages/playwright-core/src/tools/cli-daemon/program.ts`

## Constraints

- The codebase must pass ESLint and build successfully after changes.
- `browserRegistry` is already imported in the file and provides `resolveBrowsers()` and `install()` methods.
