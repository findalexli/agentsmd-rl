# MCP Server: Add Tool-Name Allowlist Parameter

## Problem

The PostHog MCP server supports a `features` query parameter that filters available tools by feature category (e.g., `?features=flags,insights`). However, MCP consumers (IDE extensions, automation scripts) sometimes need to expose only specific individual tools rather than an entire feature category.

There is currently no way to allowlist tools by their exact name. For example, a consumer might want all flag-related tools plus just `dashboard-get`, without enabling the entire dashboards feature.

## Expected Behavior

1. The MCP server should accept a new `tools` query parameter taking a comma-separated list of exact tool names (e.g., `?tools=dashboard-get,execute-sql`).
2. When only `tools` is provided, only those exact tools should be exposed.
3. When both `features` and `tools` are provided, they should compose as a union — a tool is exposed if it matches a feature category **or** its name is in the tools list.
4. After implementing the feature, update the MCP server's README to document this new filtering capability alongside the existing feature-based filtering documentation.

## Files to Look At

- `services/mcp/src/tools/toolDefinitions.ts` — tool filtering logic, `getToolsForFeatures` function and `ToolFilterOptions` interface
- `services/mcp/src/index.ts` — URL query parameter parsing for the request handler
- `services/mcp/src/mcp.ts` — `RequestProperties` type definition and MCP init method
- `services/mcp/README.md` — MCP server documentation with existing feature filtering section
