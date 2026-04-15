# Add Network Route Mocking to MCP/CLI

## Problem

The Playwright MCP server and CLI currently have no way to mock or intercept network requests. Users who want to test pages with API dependencies cannot set up route handlers for returning mock data, modifying request headers, or simulating error responses.

## Requirements

Add MCP tools and corresponding CLI commands for network route mocking:

### MCP Tools

1. **browser_route** - Set up routes that match URL patterns. The input schema must accept these fields:
   - `pattern` (string, required): URL pattern to match (e.g., "**/api/users")
   - `status` (number, optional): HTTP status code for mock responses
   - `body` (string, optional): Response body content
   - `contentType` (string, optional): Content-Type header value
   - `headers` (array of strings, optional): Headers to add in "Name: Value" format
   - `removeHeaders` (string, optional): Comma-separated header names to remove

   The tool must:
   - Fulfill with a mock response when `body` or `status` is provided
   - Continue the request with modified headers when only headers are specified

2. **browser_route_list** - List all active routes with their configuration details. When no routes are active, return exactly: `No active routes`

3. **browser_unroute** - Remove routes, either by a specific pattern or all at once. The response must include a count of removed routes (e.g., "Removed N route(s) for pattern: X" or "Removed all N route(s)").

### Route State Management

Route management state must be accessible from the browser context. This requires:
- A type exported from the context module with a `pattern: string` field
- Methods to add routes, remove routes (returning count removed), and access the routes list

The route handling must integrate with Playwright's native `browserContext.route()` and `browserContext.unroute()` APIs.

### Tool Registration

MCP tools must be registered in the browser tools module following the pattern used by other tool modules (navigate, pdf, screenshot, etc.). The route module should export its tools as a default array that can be spread into the main tools list.

### CLI Commands

Three CLI commands must be added, mapped to the MCP tools:
- `route` - Maps to `browser_route` tool
- `route-list` - Maps to `browser_route_list` tool
- `unroute` - Maps to `browser_unroute` tool

These commands must be categorized under a new `network` category in the command system. The help generator must include this category with the title "Network".

### SKILL.md Updates

Update `.claude/skills/playwright-mcp-dev/SKILL.md`:
- Add a "## Building" section with guidance on running lint and watch mode during development
- Fix the lint command from `npm run flint:mcp` to `npm run flint`
- Add a note that `test --debug` should not be used

## Files to Look At

- `packages/playwright/src/mcp/browser/` - existing MCP browser tools and context management
- `packages/playwright/src/mcp/terminal/` - CLI command definitions and help generator
- `.claude/skills/playwright-mcp-dev/SKILL.md` - development skill documentation
