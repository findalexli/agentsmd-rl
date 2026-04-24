# Expose video recording commands in Playwright MCP CLI

## Problem

The Playwright MCP server supports video recording through the browser tools layer, but these tools are not yet implemented or exposed. Additionally, the tracing tools currently use a `'tracing'` capability name, but they should be grouped under a broader `'devtools'` capability alongside the new video tools.

The terminal CLI (`playwright-cli`) also has no `video-start` / `video-stop` commands, meaning users cannot start or stop video recording from the CLI.

## Expected Behavior

### 1. New video browser tools

Create a `video.ts` module in `packages/playwright/src/mcp/browser/tools/` that defines two tools:
- One tool named `browser_start_video` that starts video recording
- One tool named `browser_stop_video` that stops video recording

Both tools must use the capability name `'devtools'`.

Import the video module in `packages/playwright/src/mcp/browser/tools.ts` and spread its exports into the `browserTools` array.

### 2. Rename `tracing` capability to `devtools`

The existing tracing tools in `packages/playwright/src/mcp/browser/tools/tracing.ts` should use `capability: 'devtools'` instead of `capability: 'tracing'`.

Update the `ToolCapability` type in `packages/playwright/src/mcp/config.d.ts` — replace `'tracing'` with `'devtools'` in the union type.

Add backward compatibility so that `--caps=tracing` still works by mapping it to `devtools`.

### 3. New terminal CLI commands

Add commands in `packages/playwright/src/mcp/terminal/commands.ts` using `declareCommand`:
- `video-start` — maps to tool name `browser_start_video`, no arguments
- `video-stop` — maps to tool name `browser_stop_video`, accepts an optional `--filename` option

### 4. CLI help update

In `packages/playwright/src/mcp/program.ts`, the `--caps` option help text (the line containing `--caps` and "possible values") must list `devtools` as a possible capability value.

### 5. Update SKILL.md documentation

The terminal CLI skill documentation at `packages/playwright/src/mcp/terminal/SKILL.md` must include `video-start` and `video-stop` commands in the DevTools section (after the "DevTools" heading).

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/video.ts` — new file for video browser tools
- `packages/playwright/src/mcp/browser/tools/tracing.ts` — capability rename
- `packages/playwright/src/mcp/browser/tools.ts` — import and register video tools
- `packages/playwright/src/mcp/config.d.ts` — ToolCapability type definition
- `packages/playwright/src/mcp/program.ts` — CLI option handling and backward compat
- `packages/playwright/src/mcp/terminal/commands.ts` — terminal command declarations
- `packages/playwright/src/mcp/terminal/SKILL.md` — CLI skill documentation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
