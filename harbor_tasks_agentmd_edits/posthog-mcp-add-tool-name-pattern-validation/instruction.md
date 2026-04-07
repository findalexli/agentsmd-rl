# Add pattern validation for MCP tool and feature names

## Problem

The MCP tool naming system only validates tool name **length** (52-character limit). There is no validation of the **character pattern** — tool names with uppercase letters, underscores, dots, spaces, or leading/trailing hyphens are silently accepted even though they break in MCP clients like Cursor (which filters out non-conforming tools) and OpenAI API (which rejects names not matching `^[a-zA-Z0-9_-]+$`).

Similarly, feature identifiers (the `feature` field in YAML configs) have no format validation at all.

The lint script (`services/mcp/scripts/lint-tool-names.ts`) only checks YAML definitions — handwritten and generated JSON definition files are not validated.

## Expected Behavior

1. **Tool names** should be validated against a lowercase kebab-case pattern (`[a-z0-9-]`, no leading/trailing hyphens) in addition to the existing 52-char length limit.
2. **Feature identifiers** should be validated against a lowercase snake_case pattern (`[a-z0-9_]`, must start with a letter).
3. Both patterns should be enforced in the **Zod schema** (`CategoryConfigSchema` in `yaml-config-schema.ts`) so violations are caught at build time.
4. The **lint script** should validate all three tool name sources: YAML definitions, handwritten JSON definitions, and generated JSON definitions.
5. After making the code changes, update the relevant **agent skill documentation** (`.agents/skills/implementing-mcp-tools/SKILL.md`) and **handbook page** (`docs/published/handbook/engineering/ai/implementing-mcp-tools.md`) to document the new naming constraints, including the pattern requirements, a client compatibility table explaining why these limits exist, and the CI enforcement mechanism.

## Files to Look At

- `services/mcp/scripts/yaml-config-schema.ts` — where validation constants and Zod schemas are defined
- `services/mcp/scripts/lint-tool-names.ts` — the lint script that validates tool names
- `.agents/skills/implementing-mcp-tools/SKILL.md` — agent skill documentation for MCP tool implementation
- `docs/published/handbook/engineering/ai/implementing-mcp-tools.md` — handbook guide for MCP tools
