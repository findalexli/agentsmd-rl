# Expose LLM Analytics Evaluation Summary as an MCP Tool

## Problem

Agents using PostHog's MCP integration cannot access the LLM evaluation results summariser. The backend endpoint `POST /api/environments/:id/llm_analytics/evaluation_summary/` is fully implemented with request/response serializers, `@extend_schema`, caching, rate limiting, and `is_ai_data_processing_approved` gating, but the corresponding MCP tool in the product's YAML config is currently disabled. There is also no skill document to help agents understand how to work with LLM evaluations.

## Expected Behavior

The evaluation summary MCP tool should be enabled and properly configured so agents can discover and invoke it. A skill document should be created for the evaluation workflow, following the existing patterns in `products/llm_analytics/skills/`.

## MCP Tool Schema Requirements

The tool to enable is `llm-analytics-evaluation-summary-create`.

Enabled MCP tools must follow this schema:

- **Tool names**: Must use kebab-case format (lowercase alphanumeric with hyphens only, e.g., `my-tool-name`), maximum 56 characters
- **Required fields for enabled tools**:
  - `enabled`: boolean set to `true`
  - `title`: non-empty string describing the tool
  - `description`: string (minimum 10 characters) explaining the tool's purpose
  - `scopes`: non-empty list of permission scopes
  - `annotations`: dictionary with three required boolean fields:
    - `readOnly`: boolean indicating if the tool only reads data
    - `destructive`: boolean indicating if the tool modifies/deletes data
    - `idempotent`: boolean indicating if repeated calls have the same effect

## Skill Document Schema Requirements

The skill to create must be named `exploring-llm-evaluations` (directory name must match this exactly).

Skill documents must follow this schema:

- **Directory name**: Must be kebab-case matching the skill's purpose
- **File location**: `SKILL.md` inside the skill directory
- **Frontmatter**: Must start with YAML frontmatter delimited by `---` containing:
  - `name`: string matching the directory name exactly
  - `description`: string explaining the skill's purpose

## Skills README Structure Requirements

The `products/llm_analytics/skills/README.md` must contain these section headers:
- `## Skills` — listing all existing skills
- `## Adding a new skill` — explaining how to add new skills

All skill directories must be referenced in the README.

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions; the evaluation summary tool entry needs to be enabled with full metadata per the schema above
- `products/llm_analytics/skills/` — existing skill documents for LLM analytics
- `products/llm_analytics/skills/README.md` — index of available skills; must reference all skill directories including the new one
- `.agents/skills/implementing-mcp-tools/SKILL.md` — guide for MCP tool YAML configuration
- `.agents/skills/writing-skills/SKILL.md` — guide for writing skill documents
