# Add MCP Server Metrics (Operation + Session Duration)

## Problem

The `@backstage/plugin-mcp-actions-backend` plugin currently has no observability into MCP server performance. There's no way to track how long individual MCP operations (like `tools/list` or `tools/call`) take, or how long client sessions last. This makes it difficult to diagnose performance issues or monitor the health of the MCP backend.

## What's Needed

Add OpenTelemetry-based metrics to the MCP actions backend plugin, following the [OTel semantic conventions for MCP](https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/). Specifically:

1. **`mcp.server.operation.duration`** — A histogram that records the duration of individual MCP operations (e.g., `tools/list`, `tools/call`). This should be instrumented in `McpService`, wrapping each request handler in timing logic. Include relevant attributes like `mcp.method.name`, `gen_ai.tool.name` (for tool calls), and `error.type` (on failure).

2. **`mcp.server.session.duration`** — A histogram that records the duration of MCP sessions from the server's perspective. This should be instrumented in the streamable HTTP router, measuring from when the POST request starts to when the connection closes or errors.

Both metrics should use the Backstage `MetricsService` (from `@backstage/backend-plugin-api/alpha`) and follow OTel conventions for bucket boundaries and attribute names.

### Metric Schema

The operation duration histogram requires these attributes on each recorded value:
- `mcp.method.name` — the MCP method being invoked (e.g., `'tools/list'`, `'tools/call'`)
- `gen_ai.tool.name` — the tool name for `tools/call` calls
- `gen_ai.operation.name` — must be `'execute_tool'` for tool invocation operations
- `error.type` — the error type; use `'tool_error'` when a `CallToolResult` has `isError=true`

The session duration histogram requires these attributes:
- `mcp.protocol.version` — the MCP protocol version in use
- `network.transport` — the transport layer (e.g., HTTP)
- `error.type` — the error type when an error occurs

### Bucket Boundaries

The histograms must use OTel-standard bucket boundaries for duration histograms. The shared `metrics.ts` module must export a `bucketBoundaries` constant containing an array that includes at minimum these values (sorted ascending): `0.01`, `0.05`, `0.1`, `1`, `10`, `60`, `300`. The minimum boundary must be `0.01` seconds and the maximum must be `300` seconds.

### Interface Definitions

The `metrics.ts` module must define two TypeScript interfaces:

- `McpServerOperationAttributes` — extending `MetricAttributes` from `@backstage/backend-plugin-api/alpha`, with required field `mcp.method.name: string`, optional fields `error.type?: string` and `gen_ai.tool.name?: string`, and recommended field `gen_ai.operation.name?: 'execute_tool'`

- `McpServerSessionAttributes` — extending `MetricAttributes` from `@backstage/backend-plugin-api/alpha`, with optional fields `mcp.protocol.version?: string`, `network.transport?: string`, and `error.type?: string`

### Instrumented Handlers

In `McpService`, both `tools/list` and `tools/call` handlers must record operation duration using the `MetricsServiceHistogram.record()` method. Use high-resolution timing (e.g., `performance.now()`) captured before the operation begins. Record the duration in a `finally` block to ensure it fires even on error, converted to seconds.

For the `tools/call` handler, the `error.type` attribute must be determined as follows:
- When an exception is thrown, use the error's `name` property
- When a `CallToolResult` has `isError=true`, use the string `'tool_error'`

The operation duration histogram is created via `metrics.createHistogram<McpServerOperationAttributes>()`, passing `'mcp.server.operation.duration'` as the metric name and an object with `advice: { explicitBucketBoundaries: bucketBoundaries }`.

In the streamable router, session duration is measured from request start to connection close/error. The session duration histogram is created via `metrics.createHistogram<McpServerSessionAttributes>()`, passing `'mcp.server.session.duration'` as the metric name. Session attributes must include `'mcp.protocol.version'` (from `LATEST_PROTOCOL_VERSION` in `@modelcontextprotocol/sdk/types.js`) and `'network.transport'` set to `'tcp'`.

### Metrics Service Integration

The Backstage `MetricsService` is accessed via `metricsServiceRef` imported from `@backstage/backend-plugin-api/alpha`. Both `McpService.create()` and `createStreamableRouter()` must accept a `metrics: MetricsService` parameter and use it to create histograms via `metrics.createHistogram()`. The `plugin.ts` file must import `metricsServiceRef`, declare a `metrics` dependency in the plugin options, and pass the metrics service to both `McpService.create()` and `createStreamableRouter()`.

## Files to Look At

- `plugins/mcp-actions-backend/src/services/McpService.ts` — Core service that handles MCP tool listing and invocation
- `plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts` — HTTP router for the streamable transport
- `plugins/mcp-actions-backend/src/plugin.ts` — Plugin wiring (needs to inject the metrics service)
- `plugins/mcp-actions-backend/src/metrics.ts` — New shared module for metrics type definitions and bucket boundaries (create this)

## Additional Requirements

- Create a shared metrics module (`metrics.ts`) that exports the bucket boundaries array and defines the metric attribute interfaces
- The plugin's README should be updated to document the new metrics so users know what telemetry data is emitted
- Don't forget the changeset file (see `.changeset/` for examples)
- Error handling must properly record `error.type` in metrics — use the OTel MCP spec distinction between thrown exceptions (use error name) and `CallToolResult` with `isError=true` (use `'tool_error'`)
