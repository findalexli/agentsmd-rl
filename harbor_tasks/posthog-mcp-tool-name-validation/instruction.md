# Add pattern validation for MCP tool names

## Problem

MCP tool names currently only have a length check (52 characters) applied to YAML-defined tools. There are two gaps:

1. **No pattern validation anywhere.** Tool names with uppercase letters, underscores, spaces, or leading/trailing hyphens are accepted silently, but they break in MCP clients. For example, Cursor silently filters out tools that don't match its naming constraints, and the OpenAI API rejects names not matching `^[a-zA-Z0-9_-]+$`.

2. **Handwritten and generated JSON definition files are not validated.** The lint script only checks YAML definitions. Tools defined in `services/mcp/schema/tool-definitions.json`, `tool-definitions-v2.json`, and `generated-tool-definitions.json` skip validation entirely.

## Expected Behavior

- Export three pattern constants from `services/mcp/scripts/yaml-config-schema.ts`:
  - `TOOL_NAME_PATTERN` — regex validating lowercase kebab-case (only `[a-z0-9-]`, no leading/trailing hyphens)
  - `FEATURE_NAME_PATTERN` — regex validating lowercase snake_case (only `[a-z0-9_]`, must start with a letter)
  - `MAX_TOOL_NAME_LENGTH` — number constant set to 52

- The `CategoryConfigSchema` Zod schema must validate:
  - Tool name keys using `.regex()` with `TOOL_NAME_PATTERN`
  - The `feature` field using `FEATURE_NAME_PATTERN`

- The lint script (`services/mcp/scripts/lint-tool-names.ts`) must:
  - Import and use `TOOL_NAME_PATTERN` for pattern validation (via a `validateToolName` function or direct regex test)
  - Validate JSON definition files: `tool-definitions.json`, `tool-definitions-v2.json`, and `generated-tool-definitions.json`

- Create a vitest test at `services/mcp/tests/unit/tool-name-validation.test.ts` that:
  - Imports `TOOL_NAME_PATTERN` and `MAX_TOOL_NAME_LENGTH` from `../../scripts/yaml-config-schema`
  - Imports `TOOL_MAP` from `@/tools` and `GENERATED_TOOL_MAP` from `@/tools/generated`
  - Validates all runtime `TOOL_MAP` and `GENERATED_TOOL_MAP` entries against `TOOL_NAME_PATTERN` and `MAX_TOOL_NAME_LENGTH`

- Update the relevant skill documentation (`.agents/skills/implementing-mcp-tools/SKILL.md`) to document:
  - A section on tool naming constraints
  - Kebab-case format for tool names (`[a-z0-9-]`, no leading/trailing hyphens)
  - The 52-character length limit and Cursor's tool name limit as the rationale
  - Snake_case format for feature identifiers (must start with a letter)

- Update the handbook page (`docs/published/handbook/engineering/ai/implementing-mcp-tools.md`) to document:
  - Feature identifier naming using snake_case
  - Character pattern validation requirements (`[a-z0-9_]` for feature identifiers)

## Files to Look At

- `services/mcp/scripts/yaml-config-schema.ts` — Zod schemas for YAML tool definitions; add pattern constants and validation here
- `services/mcp/scripts/lint-tool-names.ts` — lint script that currently only checks YAML + length; extend to cover JSON and patterns
- `services/mcp/tests/unit/tool-name-validation.test.ts` — create this vitest test for runtime tool map validation
- `.agents/skills/implementing-mcp-tools/SKILL.md` — skill documentation for MCP tool implementation
- `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` — handbook page on implementing MCP tools
