# Expose video recording commands in Playwright MCP CLI

## Problem

The Playwright MCP server supports video recording through the browser tools layer (`browser_start_video`, `browser_stop_video`), but these tools are not yet implemented or exposed. Additionally, the tracing tools currently use a `'tracing'` capability name, but they should be grouped under a broader `'devtools'` capability alongside the new video tools.

The terminal CLI (`playwright-cli`) also has no `video-start` / `video-stop` commands, meaning users cannot start or stop video recording from the CLI.

## Expected Behavior

1. **New video browser tools**: Create a `video.ts` module in `packages/playwright/src/mcp/browser/tools/` that defines `browser_start_video` and `browser_stop_video` tools under the `'devtools'` capability. Import and register these tools in `browser/tools.ts`.

2. **Rename `tracing` capability to `devtools`**: The existing tracing tools in `tracing.ts` should use `capability: 'devtools'` instead of `capability: 'tracing'`. Update the `ToolCapability` type in `config.d.ts` accordingly — replace `'tracing'` with `'devtools'`. Add backward compatibility so that `--caps=tracing` still works (by mapping it to `devtools`).

3. **New terminal CLI commands**: Add `video-start` and `video-stop` commands in `packages/playwright/src/mcp/terminal/commands.ts`, wired to the corresponding browser tools. The `video-stop` command should accept an optional `--filename` option.

4. **CLI help update**: Update the `--caps` help text in `program.ts` to list `devtools` as a possible capability value.

5. **Update the SKILL.md documentation**: The terminal CLI skill documentation at `packages/playwright/src/mcp/terminal/SKILL.md` should be updated to include the new `video-start` and `video-stop` commands in the DevTools section.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/video.ts` — new file for video browser tools
- `packages/playwright/src/mcp/browser/tools/tracing.ts` — capability rename
- `packages/playwright/src/mcp/browser/tools.ts` — import and register video tools
- `packages/playwright/src/mcp/config.d.ts` — ToolCapability type definition
- `packages/playwright/src/mcp/program.ts` — CLI option handling and backward compat
- `packages/playwright/src/mcp/terminal/commands.ts` — terminal command declarations
- `packages/playwright/src/mcp/terminal/SKILL.md` — CLI skill documentation
