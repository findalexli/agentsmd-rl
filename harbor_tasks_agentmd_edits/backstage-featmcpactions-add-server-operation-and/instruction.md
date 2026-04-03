# Add MCP Server Metrics (Operation + Session Duration)

## Problem

The `@backstage/plugin-mcp-actions-backend` plugin currently has no observability into MCP server performance. There's no way to track how long individual MCP operations (like `tools/list` or `tools/call`) take, or how long client sessions last. This makes it difficult to diagnose performance issues or monitor the health of the MCP backend.

## What's Needed

Add OpenTelemetry-based metrics to the MCP actions backend plugin, following the [OTel semantic conventions for MCP](https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/). Specifically:

1. **`mcp.server.operation.duration`** — A histogram that records the duration of individual MCP operations (e.g., `tools/list`, `tools/call`). This should be instrumented in `McpService`, wrapping each request handler in timing logic. Include relevant attributes like `mcp.method.name`, `gen_ai.tool.name` (for tool calls), and `error.type` (on failure).

2. **`mcp.server.session.duration`** — A histogram that records the duration of MCP sessions from the server's perspective. This should be instrumented in the streamable HTTP router, measuring from when the POST request starts to when the connection closes or errors.

Both metrics should use the Backstage `MetricsService` (from `@backstage/backend-plugin-api/alpha`) and follow OTel conventions for bucket boundaries and attribute names.

## Files to Look At

- `plugins/mcp-actions-backend/src/services/McpService.ts` — Core service that handles MCP tool listing and invocation
- `plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts` — HTTP router for the streamable transport
- `plugins/mcp-actions-backend/src/plugin.ts` — Plugin wiring (needs to inject the metrics service)

## Additional Requirements

- Create a shared metrics module for type definitions and bucket boundaries
- The plugin's README should be updated to document the new metrics so users know what telemetry data is emitted
- Don't forget the changeset file (see `.changeset/` for examples)
- Error handling must properly record `error.type` in metrics — use the OTel MCP spec distinction between thrown exceptions (use error name) and `CallToolResult` with `isError=true` (use `'tool_error'`)
