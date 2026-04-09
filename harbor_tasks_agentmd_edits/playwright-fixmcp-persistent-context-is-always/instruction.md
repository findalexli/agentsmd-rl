# MCP: Persistent browser context should be automatically shared

## Problem

The MCP server currently requires users to pass an explicit `--shared-browser-context` CLI flag to reuse the same browser context between connected HTTP clients when using a persistent browser context (`userDataDir`). This is confusing because when a `userDataDir` is configured, sharing the context is the only behavior that makes sense — creating separate browser instances that fight over the same data directory causes errors.

Additionally, the shared browser is eagerly created at server startup, which wastes resources if no client ever connects. And when the last client disconnects, the browser is not properly cleaned up.

## Expected Behavior

1. Remove the `--shared-browser-context` CLI flag and `sharedBrowserContext` config option entirely — they should not exist in the type definitions, CLI registration, config INI parser, or config mapping code.
2. When `userDataDir` is configured, automatically share the browser across all HTTP clients without requiring any flag.
3. Create the shared browser lazily on first client connection, not at server startup.
4. Clean up the shared browser when the last client disconnects.

After fixing the code, update the project's `CLAUDE.md` to reflect the commit convention: agents should never add Co-Authored-By lines in commit messages.

## Files to Look At

- `packages/playwright-core/src/mcp/program.ts` — MCP server setup, browser lifecycle management
- `packages/playwright-core/src/mcp/config.d.ts` — Config type definitions
- `packages/playwright-core/src/mcp/config.ts` — CLI options type and config mapping
- `packages/playwright-core/src/mcp/configIni.ts` — INI config parser longhand types
- `CLAUDE.md` — Project conventions for agent tooling
- `tests/mcp/http.spec.ts` — HTTP transport tests
- `tests/mcp/sse.spec.ts` — SSE transport tests
