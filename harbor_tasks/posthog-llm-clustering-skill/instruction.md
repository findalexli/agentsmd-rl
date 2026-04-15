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
   - Title for list tool must be exactly: **"List clustering jobs"**
   - Title for retrieve tool must be exactly: **"Get clustering job"**
   - Descriptive `description` following existing patterns

2. **Create a new skill** at `products/llm_analytics/skills/exploring-llm-clusters/`:
   - `SKILL.md` — Document how agents should investigate clusters with these exact section headings (case-sensitive):
     - `## tools` — Available tools and their purposes
     - `## how clustering works` — Event schema and cluster object shape
     - `## workflow` — Step-by-step workflows (must start with `## workflow`)
     - `## investigation patterns` — Common investigation patterns
     - `## tips` — Tips for effective cluster analysis

     The SKILL.md frontmatter must contain exactly: `name: exploring-llm-clusters`

     Document the cluster object JSON schema (inside `$ai_clusters`). Each cluster object has these exact keys:
     - `cluster_id` (integer, where `-1` represents the noise/outlier cluster)
     - `size` (integer, number of items in cluster)
     - `title` (string, descriptive name)
     - `description` (string, detailed description)
     - `traces` (object, keyed by trace/generation ID, containing objects with keys: `distance_to_centroid`, `rank`, `x`, `y`, `timestamp`, `trace_id`, `generation_id`)
     - `centroid_x` (number)
     - `centroid_y` (number)

     Example cluster object:
     ```json
     {
       "cluster_id": 0,
       "size": 42,
       "title": "User authentication flows",
       "description": "Traces involving login operations",
       "traces": {
         "<trace_or_generation_id>": {
           "distance_to_centroid": 0.123,
           "rank": 0,
           "x": -2.34,
           "y": 1.56,
           "timestamp": "2026-03-28T10:00:00Z",
           "trace_id": "abc-123",
           "generation_id": "gen-456"
         }
       },
       "centroid_x": -2.1,
       "centroid_y": 1.4
     }
     ```

   - `scripts/print_clusters.py` — Helper script that:
     - Accepts a JSON file path as CLI argument
     - Handles both direct cluster arrays and SQL result formats
     - Outputs formatted cluster summaries including:
       - Cluster count summary containing the exact text pattern `"N clusters"` (e.g., "2 clusters")
       - For each cluster: ID, title, size formatted as either `"Size: 42"` or `"42 items"` (where 42 is the actual size number)
       - For the noise cluster (`cluster_id: -1`): label it with the exact text `"(NOISE/OUTLIERS)"` or `"NOISE/OUTLIERS"`
       - Lists top traces with their `rank`, `distance_to_centroid`, and `timestamp`

3. **Update exclusion configs**:
   - `pyproject.toml` — Add `products/*/skills/*/scripts` to ruff exclusions
   - `package.json` — Update lint-staged glob to exclude skill scripts from Python formatting (pattern: `products/*/skills/*/scripts/*`)

The skill should teach agents how to:
- List recent clustering runs via SQL queries
- Parse cluster JSON data (following the schema above)
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
