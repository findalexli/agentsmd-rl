# CLI Daemon: Honor PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD Environment Variable

## Problem

The CLI daemon in `packages/playwright-core/src/tools/cli-daemon/program.ts` has the following issues:

1. **Missing env var check**: The `ensureConfiguredBrowserInstalled()` function does not check the `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` environment variable. When this variable is set to a truthy value, the function should return early without performing any browser installation.

2. **Fragile, duplicated installation logic**: Both `ensureConfiguredBrowserInstalled()` and `findOrInstallDefaultBrowser()` contain manually written browser installation code that checks for executable existence using `fs.existsSync` before calling `browserRegistry.install()`. This pattern does not resolve browser dependencies such as `ffmpeg`.

3. **Missing ffmpeg dependency**: When `findOrInstallDefaultBrowser()` finds an already-installed browser channel, it returns the channel name without ensuring that `ffmpeg` is also installed.

## Expected Behavior

1. When `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` is set to a truthy value, `ensureConfiguredBrowserInstalled()` must return immediately without performing any browser operations.

2. Both functions should use a unified approach for browser installation that resolves executables along with their dependencies.

3. `ffmpeg` must be resolved and installed when `findOrInstallDefaultBrowser()` finds an existing browser channel.

4. The chromium fallback path in `findOrInstallDefaultBrowser()` should use the same installation approach.

## File

- `packages/playwright-core/src/tools/cli-daemon/program.ts`

## Constraints

- The codebase must pass ESLint and build successfully after changes.
- `browserRegistry` is already imported in the file and provides `resolveBrowsers()` and `install()` methods.