# Enable LLM Clustering Read Tools and Add Exploring Skill

## Problem

MCP users currently have no way to explore LLM analytics clusters. The clustering infrastructure exists (models, API, frontend), but the relevant MCP tools are disabled (`enabled: false` in `products/llm_analytics/mcp/tools.yaml`) and there's no agent guidance on how to query cluster results.

## What You Need To Do

1. **Enable 2 read-only MCP tools** in `products/llm_analytics/mcp/tools.yaml`:
   - `llm-analytics-clustering-jobs-list` — list clustering job configs
   - `llm-analytics-clustering-jobs-retrieve` — get a specific job by ID

   Both should be enabled with:
   - `enabled: true`
   - `scopes: [llm_analytics:read]`
   - `annotations: { readOnly: true, destructive: false, idempotent: true }`
   - Descriptive `title` and `description` following existing patterns

2. **Create a new skill** at `products/llm_analytics/skills/exploring-llm-clusters/`:
   - `SKILL.md` — Document how agents should investigate clusters:
     - Available tools and their purposes
     - How clustering works (event schema, cluster object shape)
     - Clustering jobs configuration
     - Step-by-step workflows for exploring clusters
     - Common investigation patterns (cost analysis, error detection, etc.)
     - Tips for effective cluster analysis
   - `scripts/print_clusters.py` — Helper script to parse cluster result JSON into a readable summary

3. **Update exclusion configs**:
   - `pyproject.toml` — Add `products/*/skills/*/scripts` to ruff exclusions
   - `package.json` — Update lint-staged glob to exclude skill scripts from Python formatting

The skill should teach agents how to:
- List recent clustering runs via SQL queries
- Parse cluster JSON data
- Compute cost/latency metrics per cluster
- Drill into specific traces
- Construct UI links for visual verification

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions (needs 2 tools enabled)
- `products/llm_analytics/skills/` — existing skill directory structure
- `pyproject.toml` — ruff configuration
- `package.json` — lint-staged configuration

## Notes

- Follow the existing patterns in `tools.yaml` for title/description style
- Look at existing skills in `.agents/skills/` and `products/*/skills/` for documentation style
- The print_clusters.py script should handle both direct cluster arrays and SQL result formats
- Make sure to add proper CLI interface to the script (usage message, argument validation)
