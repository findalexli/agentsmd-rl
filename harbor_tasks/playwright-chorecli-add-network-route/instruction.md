# Add Network Route Mocking to MCP/CLI

## Problem

The Playwright MCP server and CLI currently have no way to mock or intercept network requests. Users who want to test pages with API dependencies cannot set up route handlers for returning mock data, modifying request headers, or simulating error responses.

## Expected Behavior

Add MCP tools and corresponding CLI commands for network route mocking. The implementation needs:

- A tool named `browser_route` to set up routes that match URL patterns. The input schema must accept the fields: `pattern` (string, required), `status` (number, optional), `body` (string, optional), `contentType` (string, optional), `headers` (array of strings, optional), and `removeHeaders` (string, optional). When a body or status is provided, the route should fulfill with a mock response. When only headers are specified, the route should modify headers and continue the request.
- A tool named `browser_route_list` to list all active routes with their configuration details. When no routes are active, return the string "No active routes".
- A tool named `browser_unroute` to remove routes, either by matching pattern or all at once. When removing routes, include a count in the response.
- Route management state should live in the browser context via a `RouteEntry` type exported from context.ts with a `pattern` string field, and methods `addRoute()`, `removeRoute()`, and `routes()`.
- The CLI commands should map to the corresponding MCP tools under a new `network` command category. CLI commands must be named `route`, `route-list`, and `unroute`.
- The tools must use `defineTool` and export default the tool array.

After implementing the feature, update the project's development skill file (`.claude/skills/playwright-mcp-dev/SKILL.md`) to reflect current building and testing practices — add a "## Building" section with guidance on running lint, mention that watch mode is used during development, and fix the lint command from `npm run flint:mcp` to `npm run flint`.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/` — existing MCP tool implementations (follow the pattern)
- `packages/playwright/src/mcp/browser/context.ts` — browser context management, needs route state with RouteEntry type
- `packages/playwright/src/mcp/browser/tools.ts` — tool registry; must import and spread the route module
- `packages/playwright/src/mcp/terminal/command.ts` — CLI command category types; add a `network` category
- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations for route, route-list, unroute
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — help text category list; add Network title for network category
- `.claude/skills/playwright-mcp-dev/SKILL.md` — development guidance for MCP/CLI contributors
