# Enable LLM analytics clustering tools and add exploration skill

## Problem

The LLM analytics product has mature clustering infrastructure (models, API, frontend UI), but MCP users and agents have no way to explore clustering results. The two read-only MCP tool definitions for clustering jobs exist in `products/llm_analytics/mcp/tools.yaml` but are disabled (`enabled: false`). There is also no skill to guide agents on how to query and investigate cluster results.

## Expected Behavior

1. Enable the two read-only clustering MCP tools (`llm-analytics-clustering-jobs-list` and `llm-analytics-clustering-jobs-retrieve`) in the tools YAML config with appropriate scopes, annotations, titles, and descriptions.
2. Create a new skill at `products/llm_analytics/skills/exploring-llm-clusters/` that teaches agents how to investigate LLM clusters — including the cluster event schema, SQL query patterns for querying cluster data, and investigation workflows.
3. Add a helper script (`scripts/print_clusters.py`) within the skill that parses cluster result JSON into a readable summary.
4. Update lint configuration to exclude skill scripts from ruff and lint-staged checks.

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions; clustering tools need enabling
- `.agents/skills/implementing-mcp-tools/SKILL.md` — conventions for MCP tool YAML (scopes, annotations, descriptions)
- `.agents/skills/writing-skills/SKILL.md` — conventions for creating skills (frontmatter, naming, structure)
- `pyproject.toml` — ruff exclude list needs updating for skill scripts
- `package.json` — lint-staged config needs updating for skill scripts
