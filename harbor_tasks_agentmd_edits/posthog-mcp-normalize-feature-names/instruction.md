# MCP Feature Name Inconsistency

## Problem

The MCP server has inconsistent feature naming across its tool definitions. Handcoded tools in the schema JSON files use hyphens (`error-tracking`, `llm-analytics`, `data-schema`) while generated tools use underscores (`error_tracking`). This means filtering with `?features=error-tracking` only matches the 3 handcoded tools but misses generated ones for the same product area.

Additionally, the feature filtering logic in `getToolsForFeatures()` does a direct string comparison, so `error-tracking` and `error_tracking` are treated as completely different features.

The README at `services/mcp/README.md` only documents 7 of the 28 available features, and lists them with the old hyphenated names.

## Expected Behavior

1. Feature names in the schema JSON files should be normalized to use underscores consistently
2. The feature filtering logic should handle both hyphens and underscores so existing URLs with `?features=error-tracking` continue to work (backward compatibility)
3. The README should document all available features, not just 7 of them

After fixing the code, update `services/mcp/README.md` to reflect the normalized feature names and document the complete set of available features. Note the backward-compatible behavior so users know both conventions work.

## Files to Look At

- `services/mcp/src/tools/toolDefinitions.ts` — feature filtering logic in `getToolsForFeatures()`
- `services/mcp/schema/tool-definitions.json` — v1 tool definitions with feature fields
- `services/mcp/schema/tool-definitions-all.json` — combined tool definitions
- `services/mcp/schema/tool-definitions-v2.json` — v2 tool definitions
- `services/mcp/README.md` — feature filtering documentation section
