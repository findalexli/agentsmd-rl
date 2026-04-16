# Add Network Route Commands to Playwright MCP CLI

Implement network route mocking functionality for the Playwright MCP (Model Context Protocol) system. This feature allows users to mock HTTP requests, modify response status codes, inject custom headers, and route network traffic during browser automation sessions.

## Required Features

### 1. Route Management Tools

Create a new tool module at `packages/playwright/src/mcp/browser/tools/route.ts` that provides network routing capabilities. The module must expose three tools:

**browser_route** - Mock network requests matching a URL pattern
- Must accept: `pattern` (required string, URL pattern to match)
- Must accept: `status` (optional number, HTTP status code to return)
- Must accept: `body` (optional string, response body content)
- Must accept: `contentType` (optional string, Content-Type header)
- Must accept: `headers` (optional array of strings in "Name: Value" format)
- Must accept: `removeHeaders` (optional string, comma-separated header names to remove)
- Should support both fulfilling with mock response AND modifying headers and continuing

**browser_route_list** - List all active network routes
- Read-only tool that displays all registered routes with their configuration
- Show details: pattern, status, body preview, contentType, headers added/removed

**browser_unroute** - Remove network routes
- Must accept optional `pattern` parameter (string)
- If pattern provided: remove routes matching that pattern
- If no pattern: remove ALL routes
- Must report how many routes were removed

### 2. Context Route Management

Modify `packages/playwright/src/mcp/browser/context.ts` to support route management:
- Must define a type that represents a route entry with fields for: pattern, status, body, contentType, headers to add, headers to remove, and the route handler
- Must provide a public method for retrieving the active routes array
- Must provide a public method for adding routes
- Must provide a public method for removing routes (should return number of routes removed)

### 3. Tool Registration

Modify `packages/playwright/src/mcp/browser/tools.ts` to export the route tools so they are available in the `browserTools` array.

### 4. Terminal Commands

Add terminal commands for network route management:

**Modify `packages/playwright/src/mcp/terminal/command.ts`:**
- Add 'network' to the Category type

**Modify `packages/playwright/src/mcp/terminal/commands.ts`:**
- Create three commands using `declareCommand()`:
  1. A command named `route` - Mock network requests (maps to `browser_route` tool)
     - Args: pattern (required string)
     - Options: status, body, content-type, header (repeatable), remove-header

  2. A command named `route-list` - List active routes (maps to `browser_route_list` tool)
     - No args/options

  3. A command named `unroute` - Remove routes (maps to `browser_unroute` tool)
     - Optional pattern arg

- Add all three commands with `category: 'network'`

**Modify `packages/playwright/src/mcp/terminal/helpGenerator.ts`:**
- Add network category with name `'network'` to the categories array

### 5. Documentation Update

After implementing the code changes, update the agent documentation in `.claude/skills/playwright-mcp-dev/SKILL.md`:

**Add '## Building' sections:**
- Add under the MCP section (after Testing)
- Add under the CLI section (after Testing)
- Include this exact text: "Assume watch is running at all times, run lint to see type errors"

**Update Testing sections:**
- Add this exact text to both MCP and CLI Testing sections: "Do not run test --debug"

**Update Lint section:**
- Change from `npm run flint:mcp` to `npm run flint`

## Reference

Look at existing tools for implementation patterns:
- `packages/playwright/src/mcp/browser/tools/tracing.ts` - Tool with zod schema
- `packages/playwright/src/mcp/browser/tools/navigate.ts` - Tool with handler pattern
- `packages/playwright/src/mcp/terminal/commands.ts` - Command registration patterns (see storage commands)

The Playwright route API uses:
- `browserContext.route(pattern, handler)` - intercept requests
- `browserContext.unroute(pattern, handler)` - remove interception
- `route.fulfill({ status, contentType, body })` - mock response
- `route.continue({ headers })` - continue with modified headers
