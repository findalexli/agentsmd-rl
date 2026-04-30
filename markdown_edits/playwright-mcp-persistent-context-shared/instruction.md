# Fix: Persistent browser context is always shared

## Problem

The Playwright MCP server currently has a `--shared-browser-context` CLI flag that users must explicitly set to enable sharing browser contexts between HTTP clients. When users provide a `userDataDir` (persistent browser context), they expect automatic sharing behavior without needing an extra flag.

Additionally, the current implementation eagerly creates the shared browser on server startup, even if no clients ever connect.

## Required Changes

### 1. Code Changes

Remove the `--shared-browser-context` CLI option and `sharedBrowserContext` config option from the MCP server implementation. Instead, automatically share the browser context whenever `userDataDir` is configured.

Modify the browser lifecycle in `packages/playwright-core/src/mcp/program.ts`:
- Remove the `--shared-browser-context` CLI option
- Detect shared browser need via `config.browser.userDataDir` instead of the removed flag
- Lazily create the shared browser on first client connection (not at startup)
- Clear the `sharedBrowser` reference when the last client disconnects

Update the config types in:
- `packages/playwright-core/src/mcp/config.d.ts` - remove `sharedBrowserContext` property
- `packages/playwright-core/src/mcp/config.ts` - remove from CLIOptions and configFromCLIOptions
- `packages/playwright-core/src/mcp/configIni.ts` - remove from longhandTypes

### 2. Documentation Update

After making the code changes, update the project's agent instruction file to reflect the team's commit message conventions. Add a new rule in the appropriate section of `CLAUDE.md` that addresses how to handle co-authored commits.

The rule should be placed in the Commit Convention section where other commit guidelines are documented. Look at the existing commit message format documentation in `CLAUDE.md` to understand where this new rule fits.

## Verification

The changes should:
1. Remove all traces of `sharedBrowserContext` from the codebase
2. Make persistent contexts (with `userDataDir`) automatically shared
3. Lazily initialize the shared browser only when first client connects
4. Include the updated commit message convention in `CLAUDE.md`
5. Pass TypeScript compilation checks

## Files to Modify

- `packages/playwright-core/src/mcp/program.ts`
- `packages/playwright-core/src/mcp/config.d.ts`
- `packages/playwright-core/src/mcp/config.ts`
- `packages/playwright-core/src/mcp/configIni.ts`
- `CLAUDE.md`
