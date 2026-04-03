# Enable clustering read tools and add exploring-llm-clusters skill

## Problem

MCP users working with PostHog's LLM analytics have no way to explore clustering results. The clustering infrastructure is mature — models, API endpoints, and frontend all exist — but the two read-only MCP tools for clustering jobs are disabled in the YAML config, and there's no agent skill that teaches how to query and investigate cluster results.

## What needs to happen

1. **Enable the clustering read tools** in `products/llm_analytics/mcp/tools.yaml`:
   - `llm-analytics-clustering-jobs-list` — list clustering job configurations
   - `llm-analytics-clustering-jobs-retrieve` — get a specific job by ID
   - Both should be read-only with appropriate scopes and annotations

2. **Create an `exploring-llm-clusters` skill** under `products/llm_analytics/skills/`:
   - Write a `SKILL.md` that documents the cluster event schema, SQL query patterns for exploring cluster runs, and investigation workflows
   - Include a helper script (`scripts/print_clusters.py`) that parses cluster result JSON into a readable summary
   - The skill should reference the clustering MCP tools and explain how to use `execute-sql` to query `$ai_trace_clusters` and `$ai_generation_clusters` events

3. **Exclude skill scripts from linters** — skill helper scripts don't follow the same lint rules as production code:
   - Add the skill scripts path to the ruff exclude list in `pyproject.toml`

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions for LLM analytics; the clustering tools exist but are disabled
- `products/llm_analytics/skills/` — where product skills live; see existing skills in other products for reference
- `pyproject.toml` — ruff configuration with exclude patterns
- `.agents/skills/implementing-mcp-tools/SKILL.md` — reference for how to configure MCP tools
- `.agents/skills/writing-skills/SKILL.md` — reference for how to write skills (naming conventions, structure, frontmatter)
