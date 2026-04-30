# Add response field filtering to MCP tool definitions

## Problem

MCP tool responses return full API payloads, which are large and consume significant tokens. For example, a feature flag response includes 30+ fields (`experiment_set`, `surveys`, `analytics_dashboards`, etc.) when an agent typically only needs `id`, `key`, `name`, and `status`. There is currently no way to control which response fields are returned to the MCP client.

## Expected Behavior

The YAML tool definition schema should support a `response` config object with `include` and `exclude` field lists that accept wildcard dot-path patterns (e.g., `filters.groups.*.key`). The two modes should be mutually exclusive. For list endpoints, filtering should be applied per-item on the `results` array.

The implementation needs:
1. **Runtime helpers** in `services/mcp/src/tools/tool-utils.ts` — functions that can pick or omit fields from response objects, supporting dot-path patterns with `*` wildcards for iterating arrays/object keys
2. **Schema validation** in `services/mcp/scripts/yaml-config-schema.ts` — a Zod schema for the new `response` config object
3. **Code generation** in `services/mcp/scripts/generate-tools.ts` — a function that generates filtering code between the API call and `_posthogUrl` enrichment. The enrichment step (`buildEnrichment`) should operate on the filtered result when filtering is active
4. **Feature flag usage** — apply `response.include` to `feature-flag-get-all` in `products/feature_flags/mcp/tools.yaml` to return only `id`, `key`, `name`, `updated_at`, `status`, and `tags`

After implementing the code, update the relevant documentation to reflect the new `response` config option. The implementing-mcp-tools skill, the definitions README, and the handbook reference all document the YAML schema and should be updated.

## Files to Look At

- `services/mcp/src/tools/tool-utils.ts` — runtime utilities for MCP tools; add pick/omit helpers here
- `services/mcp/scripts/yaml-config-schema.ts` — Zod schemas for YAML tool definitions
- `services/mcp/scripts/generate-tools.ts` — code generation for tool handlers
- `products/feature_flags/mcp/tools.yaml` — feature flag tool definitions
- `.agents/skills/implementing-mcp-tools/SKILL.md` — skill documentation for MCP tool implementation
- `services/mcp/definitions/README.md` — YAML schema reference documentation
- `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` — handbook documentation
