# Add Network Route Mocking to MCP Browser Tools and CLI

## Problem

The Playwright MCP tools currently support navigating, clicking, typing, screenshots, and many other browser interactions — but there's no way to mock or intercept network requests. Users who need to test against specific API responses, inject custom headers, or simulate error statuses have to resort to running arbitrary code via `browser_run_code`, which is cumbersome and defeats the purpose of having structured MCP tools.

## Expected Behavior

There should be a set of MCP browser tools and corresponding CLI commands for network route management:

1. **A tool to set up routes** that mock network requests matching a URL pattern. It should support:
   - Returning a custom response body and status code (response mocking / fulfillment)
   - Adding or removing request headers (request modification)
   - A URL pattern parameter (glob-style, e.g. `**/api/users`)
   - Optional content-type specification

2. **A tool to list active routes** — showing all currently registered route patterns and their configurations.

3. **A tool to remove routes** — either a specific route by pattern, or all routes at once.

Each MCP tool needs a corresponding CLI command, grouped under a new `network` CLI category.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/` — existing tool implementations (see `navigate.ts`, `network.ts` for patterns)
- `packages/playwright/src/mcp/browser/tools.ts` — tool registration
- `packages/playwright/src/mcp/browser/context.ts` — shared browser context (route state should live here)
- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations
- `packages/playwright/src/mcp/terminal/command.ts` — CLI category type definition
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — help text categories
- `.claude/skills/playwright-mcp-dev/SKILL.md` — developer instructions for adding MCP tools and CLI commands

## Notes

- Follow the patterns established by existing tools (see the SKILL.md for the checklist).
- After implementing the code changes, update the developer skill documentation (`.claude/skills/playwright-mcp-dev/SKILL.md`) to reflect what you've learned about the build and test workflow — specifically around using the watch process, lint for type checking, and the correct lint command name. Also note any testing flags that should be avoided.
