#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if [ -f "products/llm_analytics/skills/exploring-llm-clusters/SKILL.md" ]; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Enable clustering-jobs-list in tools.yaml ---
python3 -c "
import re
p = 'products/llm_analytics/mcp/tools.yaml'
t = open(p).read()

# Replace clustering-jobs-list block
old_list = '''    llm-analytics-clustering-jobs-list:
        operation: llm_analytics_clustering_jobs_list
        enabled: false'''
new_list = '''    llm-analytics-clustering-jobs-list:
        operation: llm_analytics_clustering_jobs_list
        enabled: true
        scopes:
            - llm_analytics:read
        annotations:
            readOnly: true
            destructive: false
            idempotent: true
        title: List clustering jobs
        description: >
            List all clustering job configurations for the current team (max 5 per team).
            Each job defines an analysis level (trace or generation) and event filters that
            scope which traces are included in clustering runs. Cluster results are stored
            as \\\$ai_trace_clusters and \\\$ai_generation_clusters events \u2014 use docs-search or
            execute-sql to query them.'''
t = t.replace(old_list, new_list)

# Replace clustering-jobs-retrieve block
old_ret = '''    llm-analytics-clustering-jobs-retrieve:
        operation: llm_analytics_clustering_jobs_retrieve
        enabled: false'''
new_ret = '''    llm-analytics-clustering-jobs-retrieve:
        operation: llm_analytics_clustering_jobs_retrieve
        enabled: true
        scopes:
            - llm_analytics:read
        annotations:
            readOnly: true
            destructive: false
            idempotent: true
        title: Get clustering job
        description: >
            Retrieve a specific clustering job configuration by ID. Returns the job name,
            analysis level (trace or generation), event filters, enabled status, and timestamps.'''
t = t.replace(old_ret, new_ret)

open(p, 'w').write(t)
print('tools.yaml updated')
"

# --- 2. Add ruff exclusion for skill scripts in pyproject.toml ---
sed -i '/^    "\.\/posthog\/hogql\/grammar",$/a\    "products/*/skills/*/scripts",' pyproject.toml

# --- 3. Update lint-staged glob in package.json to exclude skill scripts ---
python3 -c "
p = 'package.json'
t = open(p).read()
old = '!(posthog/hogql/grammar/*|posthog/personhog_client/proto/generated/*)*.{py,pyi}'
new = '!(posthog/hogql/grammar/*|posthog/personhog_client/proto/generated/*|products/*/skills/*/scripts/*)*.{py,pyi}'
t = t.replace(old, new)
open(p, 'w').write(t)
print('package.json updated')
"

# --- 4. Create exploring-llm-clusters skill ---
mkdir -p products/llm_analytics/skills/exploring-llm-clusters/scripts

cat > products/llm_analytics/skills/exploring-llm-clusters/SKILL.md <<'SKILLEOF'
---
name: exploring-llm-clusters
description: 'Investigate LLM analytics clusters — understand usage patterns in AI/LLM traffic, compare cluster behavior, compute cost/latency metrics, and drill into individual traces within clusters.'
---

# Exploring LLM clusters

Use this skill when investigating LLM analytics clusters —
understanding what patterns exist in your AI/LLM traffic,
comparing cluster behavior, and drilling into individual clusters.

## Tools

| Tool                                             | Purpose                                         |
| ------------------------------------------------ | ----------------------------------------------- |
| `posthog:llm-analytics-clustering-jobs-list`     | List clustering job configurations for the team |
| `posthog:llm-analytics-clustering-jobs-retrieve` | Get a specific clustering job by ID             |
| `posthog:execute-sql`                            | Query cluster run events and compute metrics    |
| `posthog:query-llm-traces-list`                  | Find traces belonging to a cluster              |
| `posthog:query-llm-trace`                        | Inspect a specific trace in detail              |

## How clustering works

PostHog clusters LLM traces (or individual generations) by embedding similarity.
A Temporal workflow runs periodically or on-demand, producing cluster events stored as
`$ai_trace_clusters` (trace-level) or `$ai_generation_clusters` (generation-level).

Each cluster event contains:

- `$ai_clustering_run_id` — unique run identifier (format: `<team_id>_<level>_<YYYYMMDD>_<HHMMSS>[_<job_id>]`)
- `$ai_clustering_level` — `"trace"` or `"generation"`
- `$ai_window_start` / `$ai_window_end` — time window analyzed
- `$ai_total_items_analyzed` — number of traces/generations processed
- `$ai_clusters` — JSON array of cluster objects
- `$ai_clustering_params` — algorithm parameters used

### Cluster object shape (inside `$ai_clusters`)

```json
{
  "cluster_id": 0,
  "size": 42,
  "title": "User authentication flows",
  "description": "Traces involving login, signup, and token refresh operations",
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

- `cluster_id: -1` is the **noise/outlier** cluster (items that didn't fit any cluster)
- Items in `traces` are keyed by trace ID (trace-level) or generation event UUID (generation-level)
- `rank` orders items by proximity to centroid (0 = closest)
- `x`, `y` are 2D coordinates for visualization (UMAP/PCA/t-SNE reduced)

## Clustering jobs

Each team can have up to 5 clustering jobs. A job defines:

- **name** — human-readable label
- **analysis_level** — `"trace"` or `"generation"`
- **event_filters** — property filters scoping which traces are included
- **enabled** — whether the job runs on schedule

Default jobs named `"Default - trace"` and `"Default - generation"` are auto-created
and disabled when a custom job is created for the same level.

## Workflow: explore clusters

### Step 1 — List recent clustering runs

```sql
posthog:execute-sql
SELECT
    JSONExtractString(properties, '$ai_clustering_run_id') as run_id,
    JSONExtractString(properties, '$ai_clustering_level') as level,
    JSONExtractString(properties, '$ai_window_start') as window_start,
    JSONExtractString(properties, '$ai_window_end') as window_end,
    JSONExtractInt(properties, '$ai_total_items_analyzed') as total_items,
    timestamp
FROM events
WHERE event IN ('$ai_trace_clusters', '$ai_generation_clusters')
    AND timestamp >= now() - INTERVAL 7 DAY
ORDER BY timestamp DESC
LIMIT 10
```

### Step 2 — Get clusters from a specific run

```sql
posthog:execute-sql
SELECT
    JSONExtractString(properties, '$ai_clustering_run_id') as run_id,
    JSONExtractString(properties, '$ai_clustering_level') as level,
    JSONExtractString(properties, '$ai_clustering_job_id') as job_id,
    JSONExtractString(properties, '$ai_clustering_job_name') as job_name,
    JSONExtractString(properties, '$ai_window_start') as window_start,
    JSONExtractString(properties, '$ai_window_end') as window_end,
    JSONExtractInt(properties, '$ai_total_items_analyzed') as total_items,
    JSONExtractRaw(properties, '$ai_clusters') as clusters,
    JSONExtractRaw(properties, '$ai_clustering_params') as params
FROM events
WHERE event IN ('$ai_trace_clusters', '$ai_generation_clusters')
    AND JSONExtractString(properties, '$ai_clustering_run_id') = '<run_id>'
LIMIT 1
```

The `clusters` field is a JSON array. Parse it to see cluster titles, sizes, and descriptions.

**Important:** The clusters JSON can be very large (thousands of trace IDs with coordinates).
When the result is too large for inline display, it auto-persists to a file.
Use `print_clusters.py` from [scripts/](./scripts/) to get a readable summary.

### Step 3 — Compute metrics for clusters

For trace-level clusters, compute cost/latency/token metrics:

```sql
posthog:execute-sql
SELECT
    JSONExtractString(properties, '$ai_trace_id') as trace_id,
    sum(toFloat(properties.$ai_total_cost_usd)) as total_cost,
    max(toFloat(properties.$ai_latency)) as latency,
    sum(toInt(properties.$ai_input_tokens)) as input_tokens,
    sum(toInt(properties.$ai_output_tokens)) as output_tokens,
    countIf(properties.$ai_is_error = 'true') as error_count
FROM events
WHERE event IN ('$ai_generation', '$ai_embedding', '$ai_span')
    AND timestamp >= parseDateTimeBestEffort('<window_start>')
    AND timestamp <= parseDateTimeBestEffort('<window_end>')
    AND JSONExtractString(properties, '$ai_trace_id') IN ('<trace_id_1>', '<trace_id_2>', ...)
GROUP BY trace_id
```

### Step 4 — Drill into specific traces

Once you've identified interesting clusters, use the trace tools to inspect individual traces:

```json
posthog:query-llm-trace
{
  "traceId": "<trace_id_from_cluster>",
  "dateRange": {"date_from": "<window_start>", "date_to": "<window_end>"}
}
```

## Investigation patterns

### "What kinds of LLM usage do we have?"

1. List recent clustering runs (Step 1)
2. Load the latest run's clusters (Step 2)
3. Review cluster titles and descriptions — each represents a distinct usage pattern
4. Compare cluster sizes to understand traffic distribution

### "Which cluster is most expensive / slowest?"

1. Load clusters from a run (Step 2)
2. Extract trace IDs from each cluster
3. Compute metrics per cluster (Step 3)
4. Aggregate: `avg(cost)`, `avg(latency)`, `sum(cost)` per cluster
5. Compare across clusters

### "What's in this cluster?"

1. Load the cluster's traces (from the `traces` field)
2. Sort by `rank` (closest to centroid = most representative)
3. Inspect the top 3-5 traces via `query-llm-trace` to understand the pattern
4. Check the cluster `title` and `description` for the AI-generated summary

### "Are there error-heavy clusters?"

1. Compute metrics (Step 3) with `error_count`
2. Calculate error rate per cluster: `items_with_errors / total_items`
3. Focus on clusters with high error rates
4. Drill into errored traces to find root causes

## Constructing UI links

- **Clusters overview**: `https://app.posthog.com/llm-analytics/clusters`
- **Specific run**: `https://app.posthog.com/llm-analytics/clusters/<url_encoded_run_id>`
- **Cluster detail**: `https://app.posthog.com/llm-analytics/clusters/<url_encoded_run_id>/<cluster_id>`

Always surface these links so the user can verify visually in the PostHog UI.

## Tips

- Always set a time range in SQL queries — cluster events without time bounds are slow
- Start with run listing to orient, then drill into specific clusters
- Cluster titles and descriptions are AI-generated summaries — verify by inspecting traces
- The noise cluster (`cluster_id: -1`) contains outliers that didn't fit any pattern
- Use `llm-analytics-clustering-jobs-list` to understand what clustering configs are active
- Trace IDs in clusters can be used directly with `query-llm-trace` for deep inspection
- For large clusters, inspect the top-ranked traces (closest to centroid) for representative examples
SKILLEOF

# --- 5. Create print_clusters.py ---
cat > products/llm_analytics/skills/exploring-llm-clusters/scripts/print_clusters.py <<'PYSCRIPTEOF'
"""Print a summary of clusters from a clustering run result."""

import json
import sys


def load_result_file(path):
    with open(path) as f:
        raw = json.load(f)
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and raw[0].get("type") == "text":
        raw = json.loads(raw[0]["text"])
    return raw


def parse_result(raw):
    """Extract clusters array and run metadata from various result shapes."""
    meta: dict[str, str | int | float] = {}
    clusters = []

    # Direct clusters array
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "cluster_id" in raw[0]:
        return raw, meta

    # SQL result — look for clusters JSON and metadata columns
    if isinstance(raw, dict) and "results" in raw:
        columns = raw.get("columns", [])
        for row in raw["results"]:
            for i, cell in enumerate(row):
                col_name = columns[i] if i < len(columns) else ""
                # Extract run metadata from known columns
                if isinstance(cell, str) and col_name in (
                    "run_id", "level", "job_id", "job_name",
                    "window_start", "window_end", "total_items",
                ):
                    meta[col_name] = cell
                elif isinstance(cell, (int, float)) and col_name == "total_items":
                    meta[col_name] = cell
                # Find the clusters JSON
                if isinstance(cell, str) and cell.startswith("["):
                    try:
                        parsed = json.loads(cell)
                        if isinstance(parsed, list) and parsed and "cluster_id" in parsed[0]:
                            clusters = parsed
                    except (json.JSONDecodeError, TypeError):
                        continue
    return clusters, meta


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python print_clusters.py <result_file_path>")
        sys.exit(1)

    data = load_result_file(sys.argv[1])
    clusters, meta = parse_result(data)

    if not clusters:
        print("No clusters found in file.")
        sys.exit(1)

    clusters.sort(key=lambda c: c.get("size", 0), reverse=True)

    print(f"\n{'='*80}")
    if meta:
        if meta.get("job_name"):
            print(f"  Job: {meta['job_name']}")
        if meta.get("level"):
            print(f"  Level: {meta['level']}")
        if meta.get("run_id"):
            print(f"  Run: {meta['run_id']}")
        if meta.get("job_id"):
            print(f"  Job ID: {meta['job_id']}")
        if meta.get("window_start") or meta.get("window_end"):
            print(f"  Window: {meta.get('window_start', '?')} → {meta.get('window_end', '?')}")
        if meta.get("total_items"):
            print(f"  Items analyzed: {meta['total_items']}")
        print(f"  ---")
    print(f"  {len(clusters)} clusters, {sum(c.get('size', 0) for c in clusters)} total items")
    print(f"{'='*80}")

    for c in clusters:
        cid = c.get("cluster_id", "?")
        label = "(NOISE/OUTLIERS)" if cid == -1 else ""
        title = c.get("title", f"Cluster {cid}")
        size = c.get("size", 0)
        desc = c.get("description", "")

        print(f"\n  Cluster {cid} {label}")
        print(f"  Title: {title}")
        print(f"  Size:  {size} items")
        if desc:
            print(f"  Desc:  {desc[:200]}{'...' if len(desc) > 200 else ''}")

        # Show top 5 traces by rank
        traces = c.get("traces", {})
        ranked = sorted(traces.items(), key=lambda t: t[1].get("rank", 999))[:5]
        if ranked:
            print(f"  Top traces (by centroid proximity):")
            for tid, info in ranked:
                dist = info.get("distance_to_centroid")
                ts = info.get("timestamp", "?")
                dist_str = f"{dist:.4f}" if isinstance(dist, (int, float)) else "?"
                print(f"    #{info.get('rank', '?'):>3}  {tid}  dist={dist_str}  {ts}")
PYSCRIPTEOF

echo "Patch applied successfully."
