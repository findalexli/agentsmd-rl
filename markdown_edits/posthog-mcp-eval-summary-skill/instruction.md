# Expose LLM evaluation summary as an MCP tool and document it

## Problem

The LLM Analytics product has a backend endpoint for generating AI-powered summaries of evaluation results (`POST /api/environments/:id/llm_analytics/evaluation_summary/`), but the corresponding MCP tool in `products/llm_analytics/mcp/tools.yaml` is scaffolded with `enabled: false`. Agents using PostHog's MCP server cannot access this functionality.

Additionally, there is no skill documentation teaching agents how to work with LLM evaluations — how to investigate failing evaluations, run evaluations against specific generations, or generate summaries of pass/fail patterns.

## Expected Behavior

1. The `llm-analytics-evaluation-summary-create` tool in `products/llm_analytics/mcp/tools.yaml` should be enabled with proper configuration: scopes (`llm_analytics:write`), annotations (not readOnly, not destructive, idempotent), `requires_ai_consent: true`, and a descriptive title and description of the tool's inputs and outputs.

2. After enabling the tool in the YAML, run `hogli build:openapi` (or equivalent) to regenerate the TypeScript tool handler and Zod schemas from the OpenAPI spec. The generated files under `services/mcp/src/generated/` and `services/mcp/src/tools/generated/` must include the new tool.

3. Create a new skill at `products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md` that documents how to work with LLM evaluations. The skill should cover both evaluation types (`hog` and `llm_judge`), explain when to use each, and provide workflow guidance for investigating failing evaluations, running evaluations against specific generations, and generating AI-powered summaries.

4. Update `products/llm_analytics/skills/README.md` to list the new skill alongside the existing ones.

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions; the evaluation-summary tool entry needs to be flipped from disabled to enabled with full metadata
- `products/llm_analytics/skills/README.md` — skill registry that needs the new skill entry
- `products/llm_analytics/skills/exploring-llm-traces/SKILL.md` — example of an existing skill for reference on structure and style
- `.agents/skills/implementing-mcp-tools/SKILL.md` — guide on how MCP tools are configured and generated
- `.agents/skills/writing-skills/SKILL.md` — guide on writing agent skills (naming conventions, frontmatter, structure)
