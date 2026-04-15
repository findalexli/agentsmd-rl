# Add pattern validation for MCP tool names

## Problem

MCP tool names currently only have a length check applied to YAML-defined tools. There are two gaps:

1. **No pattern validation anywhere.** Tool names with uppercase letters, underscores, spaces, or leading/trailing hyphens are accepted silently, but they break in MCP clients. For example, Cursor silently filters out tools that don't match its naming constraints, and the OpenAI API rejects names not matching `^[a-zA-Z0-9_-]+$`.

2. **Handwritten and generated JSON definition files are not validated.** The lint script only checks YAML definitions. Tools defined in `services/mcp/schema/tool-definitions.json`, `tool-definitions-v2.json`, and `generated-tool-definitions.json` skip validation entirely.

## Expected Behavior

The following must be implemented to enforce consistent tool naming across the MCP system:

### 1. Pattern Constants in yaml-config-schema.ts

Export three validation constants from `services/mcp/scripts/yaml-config-schema.ts`:

- `TOOL_NAME_PATTERN` — a regex that validates lowercase kebab-case tool names. Valid names contain only lowercase letters, digits, and hyphens. They must not start or end with a hyphen. Examples: `cohorts-create` should be valid; `-leading`, `trailing-`, `UPPERCASE`, `has space`, `under_score` should be rejected.

- `FEATURE_NAME_PATTERN` — a regex that validates lowercase snake_case feature identifiers. Valid identifiers contain only lowercase letters, digits, and underscores, and must start with a letter (not a digit or underscore). Examples: `error_tracking`, `feature_flags`, `surveys` should be valid; `_leading`, `1starts_with_digit`, `UPPER`, `kebab-case` should be rejected.

- `MAX_TOOL_NAME_LENGTH` — a number constant representing the maximum allowed length for tool names. The MCP specification and Cursor client impose a limit; use 52 as the value.

### 2. Zod Schema Validation

The `CategoryConfigSchema` must validate:
- Tool name record keys using pattern validation with `TOOL_NAME_PATTERN`
- The `feature` field using `FEATURE_NAME_PATTERN`

### 3. Lint Script Updates

The lint script (`services/mcp/scripts/lint-tool-names.ts`) must:
- Import `TOOL_NAME_PATTERN` and use it for pattern validation (either via a `validateToolName` function or by directly using the pattern's test method)
- Validate JSON definition files: `tool-definitions.json`, `tool-definitions-v2.json`, and `generated-tool-definitions.json` in addition to YAML files

### 4. Unit Tests

Create a vitest test at `services/mcp/tests/unit/tool-name-validation.test.ts` that:
- Imports `TOOL_NAME_PATTERN` and `MAX_TOOL_NAME_LENGTH` from the schema module
- Imports `TOOL_MAP` from the tools module and `GENERATED_TOOL_MAP` from the generated tools module
- Validates all entries in both `TOOL_MAP` and `GENERATED_TOOL_MAP` against `TOOL_NAME_PATTERN` and `MAX_TOOL_NAME_LENGTH`

### 5. Documentation Updates

Update `.agents/skills/implementing-mcp-tools/SKILL.md` to document:
- A section on tool naming constraints
- Kebab-case format requirements for tool names (lowercase alphanumeric and hyphens only; no leading/trailing hyphens)
- The 52-character length limit and Cursor's tool name limit as the rationale
- Snake_case format for feature identifiers (must start with a letter)

Update `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` to document:
- Feature identifier naming using snake_case
- Character pattern validation requirements for feature identifiers (lowercase alphanumeric and underscores only)

## Files to Look At

- `services/mcp/scripts/yaml-config-schema.ts` — Zod schemas for YAML tool definitions; add pattern constants and validation here
- `services/mcp/scripts/lint-tool-names.ts` — lint script that currently only checks YAML + length; extend to cover JSON and patterns
- `services/mcp/tests/unit/tool-name-validation.test.ts` — create this vitest test for runtime tool map validation
- `.agents/skills/implementing-mcp-tools/SKILL.md` — skill documentation for MCP tool implementation
- `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` — handbook page on implementing MCP tools
