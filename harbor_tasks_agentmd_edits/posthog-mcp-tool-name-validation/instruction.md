# Add pattern validation for MCP tool names

## Problem

MCP tool names currently only have a length check (52 characters) applied to YAML-defined tools. There are two gaps:

1. **No pattern validation anywhere.** Tool names with uppercase letters, underscores, spaces, or leading/trailing hyphens are accepted silently, but they break in MCP clients. For example, Cursor silently filters out tools that don't match its naming constraints, and the OpenAI API rejects names not matching `^[a-zA-Z0-9_-]+$`.

2. **Handwritten and generated JSON definition files are not validated.** The lint script (`services/mcp/scripts/lint-tool-names.ts`) only checks YAML definitions. Tools defined in `services/mcp/schema/tool-definitions.json`, `tool-definitions-v2.json`, and `generated-tool-definitions.json` skip validation entirely.

## Expected Behavior

- Tool names should be validated against a **lowercase kebab-case** pattern (only `[a-z0-9-]`, no leading/trailing hyphens) — this is the safe intersection across all MCP clients.
- Feature identifiers (the `feature` field in YAML configs) should be validated as **lowercase snake_case** (only `[a-z0-9_]`, must start with a letter).
- Both pattern constants should be exported from `services/mcp/scripts/yaml-config-schema.ts` so they can be reused across the codebase.
- The `CategoryConfigSchema` Zod schema should validate tool name keys and the `feature` field at parse time using these patterns.
- The lint script should be extended to also validate JSON definition files (not just YAML).
- A vitest test should validate all runtime `TOOL_MAP` and `GENERATED_TOOL_MAP` entries against these constraints.

After making the code changes, update the relevant skill documentation (`.agents/skills/implementing-mcp-tools/SKILL.md`) and the handbook page (`docs/published/handbook/engineering/ai/implementing-mcp-tools.md`) to document the naming constraints, including the character patterns, the rationale for the 52-char limit, and MCP client compatibility details. The existing docs only mention the length limit — they should now also cover the pattern requirements and feature identifier format.

## Files to Look At

- `services/mcp/scripts/yaml-config-schema.ts` — Zod schemas for YAML tool definitions; add pattern constants and validation here
- `services/mcp/scripts/lint-tool-names.ts` — lint script that currently only checks YAML + length; extend to cover JSON and patterns
- `services/mcp/tests/unit/` — add a vitest test for runtime tool map validation
- `.agents/skills/implementing-mcp-tools/SKILL.md` — skill documentation for MCP tool implementation
- `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` — handbook page on implementing MCP tools
