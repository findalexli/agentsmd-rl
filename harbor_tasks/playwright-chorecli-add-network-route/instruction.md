# Add Network Route Mocking to MCP/CLI

## Problem

The Playwright MCP server and CLI currently have no way to mock or intercept network requests. Users who want to test pages with API dependencies cannot set up route handlers for returning mock data, modifying request headers, or simulating error responses.

## Expected Behavior

Add MCP tools and corresponding CLI commands for network route mocking. The implementation needs:

- A tool to set up routes that match URL patterns. When a body or status is provided, the route should fulfill with a mock response. When only headers are specified, the route should modify headers and continue the request.
- A tool to list all active routes with their configuration details.
- A tool to remove routes, either by matching pattern or all at once.

Route management state should live in the browser context. The CLI commands should map to the corresponding MCP tools under a new command category. Follow the conventions established by existing MCP tools and CLI commands in the codebase.

After implementing the feature, update the project's development skill file (`.claude/skills/playwright-mcp-dev/SKILL.md`) to reflect current building and testing practices — the existing guidance has some gaps and an outdated lint command.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/` — existing MCP tool implementations (follow the pattern)
- `packages/playwright/src/mcp/browser/context.ts` — browser context management, needs route state
- `packages/playwright/src/mcp/browser/tools.ts` — tool registry
- `packages/playwright/src/mcp/terminal/command.ts` — CLI command category types
- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — help text category list
- `.claude/skills/playwright-mcp-dev/SKILL.md` — development guidance for MCP/CLI contributors
