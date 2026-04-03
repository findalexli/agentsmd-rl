#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'normalizeFeatureName' services/mcp/src/tools/toolDefinitions.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Normalize feature names in schema files (hyphens → underscores)
for f in services/mcp/schema/tool-definitions.json services/mcp/schema/tool-definitions-all.json services/mcp/schema/tool-definitions-v2.json; do
    sed -i 's/"feature": "error-tracking"/"feature": "error_tracking"/g' "$f"
    sed -i 's/"feature": "llm-analytics"/"feature": "llm_analytics"/g' "$f"
    sed -i 's/"feature": "data-schema"/"feature": "data_schema"/g' "$f"
done

# 2. Add normalizeFeatureName function and update filtering logic in toolDefinitions.ts
python3 - <<'PYEOF'
import re

path = "services/mcp/src/tools/toolDefinitions.ts"
src = open(path).read()

# Add normalizeFeatureName function before getToolsForFeatures
old_fn = "export function getToolsForFeatures"
new_fn = """function normalizeFeatureName(name: string): string {
    return name.replace(/-/g, '_')
}

export function getToolsForFeatures"""
src = src.replace(old_fn, new_fn)

# Replace the old feature filtering logic
old_filter = """    // Filter by features if provided
    if (features && features.length > 0) {
        entries = entries.filter(([_, definition]) => definition.feature && features.includes(definition.feature))
    }"""
new_filter = """    // Filter by features if provided. Normalize hyphens to underscores so that
    // both "error-tracking" and "error_tracking" match regardless of convention.
    if (features && features.length > 0) {
        const normalizedFeatures = new Set(features.map(normalizeFeatureName))
        entries = entries.filter(
            ([_, definition]) => definition.feature && normalizedFeatures.has(normalizeFeatureName(definition.feature))
        )
    }"""
src = src.replace(old_filter, new_filter)

open(path, "w").write(src)
print("toolDefinitions.ts patched")
PYEOF

# 3. Update README.md feature filtering section
python3 - <<'PYEOF'
path = "services/mcp/README.md"
content = open(path).read()

old_section = """You can limit which tools are available by adding query parameters to the MCP URL:

```text
https://mcp.posthog.com/mcp?features=flags,workspace
```

Available features:

- `workspace` - Organization and project management
- `error-tracking` - [Error monitoring and debugging](https://posthog.com/docs/errors)
- `dashboards` - [Dashboard creation and management](https://posthog.com/docs/product-analytics/dashboards)
- `insights` - [Analytics insights and SQL queries](https://posthog.com/docs/product-analytics/insights)
- `experiments` - [A/B testing experiments](https://posthog.com/docs/experiments)
- `flags` - [Feature flag management](https://posthog.com/docs/feature-flags)
- `llm-analytics` - [LLM usage and cost tracking](https://posthog.com/docs/llm-analytics)
- `docs` - PostHog documentation search

To view which tools are available per feature, see our [documentation](https://posthog.com/docs/model-context-protocol) or alternatively check out `schema/tool-definitions.json`,"""

new_section = """You can limit which tools are available by adding query parameters to the MCP URL. If no features are specified, all tools are available. When features are specified, only tools matching those features are exposed.

```text
https://mcp.posthog.com/mcp?features=flags,workspace,dashboards
```

Available features:

| Feature                  | Description                                                                                               |
| ------------------------ | --------------------------------------------------------------------------------------------------------- |
| `workspace`              | Organization and project management                                                                       |
| `actions`                | [Action definitions](https://posthog.com/docs/data/actions)                                               |
| `activity_logs`          | Activity log viewing                                                                                      |
| `alerts`                 | [Alert management](https://posthog.com/docs/product-analytics/alerts)                                     |
| `annotations`            | [Annotation management](https://posthog.com/docs/product-analytics/annotations)                           |
| `cohorts`                | [Cohort management](https://posthog.com/docs/data/cohorts)                                                |
| `dashboards`             | [Dashboard creation and management](https://posthog.com/docs/product-analytics/dashboards)                |
| `data_schema`            | Data schema exploration                                                                                   |
| `data_warehouse`         | [Data warehouse management](https://posthog.com/docs/data-warehouse)                                      |
| `debug`                  | Debug and diagnostic tools                                                                                |
| `docs`                   | PostHog documentation search                                                                              |
| `early_access_features`  | [Early access feature management](https://posthog.com/docs/feature-flags/early-access-feature-management) |
| `error_tracking`         | [Error monitoring and debugging](https://posthog.com/docs/error-tracking)                                 |
| `events`                 | Event and property definitions                                                                            |
| `experiments`            | [A/B testing experiments](https://posthog.com/docs/experiments)                                           |
| `flags`                  | [Feature flag management](https://posthog.com/docs/feature-flags)                                         |
| `hog_functions`          | [CDP function management](https://posthog.com/docs/cdp)                                                   |
| `hog_function_templates` | CDP function template browsing                                                                            |
| `insights`               | [Analytics insights](https://posthog.com/docs/product-analytics/insights)                                 |
| `llm_analytics`          | [LLM analytics evaluations](https://posthog.com/docs/ai-engineering)                                      |
| `prompts`                | [LLM prompt management](https://posthog.com/docs/ai-engineering)                                          |
| `logs`                   | [Log querying](https://posthog.com/docs/ai-engineering/observability)                                     |
| `notebooks`              | [Notebook management](https://posthog.com/docs/notebooks)                                                 |
| `persons`                | [Person and group management](https://posthog.com/docs/data/persons)                                      |
| `reverse_proxy`          | Reverse proxy record management                                                                           |
| `search`                 | Entity search across the project                                                                          |
| `sql`                    | SQL query execution                                                                                       |
| `surveys`                | [Survey management](https://posthog.com/docs/surveys)                                                     |
| `workflows`              | [Workflow management](https://posthog.com/docs/cdp)                                                       |

> **Note:** Hyphens and underscores are treated as equivalent in feature names (e.g., `error-tracking` and `error_tracking` both work).

To view which tools are available per feature, see our [documentation](https://posthog.com/docs/model-context-protocol) or check `schema/tool-definitions-all.json`."""

content = content.replace(old_section, new_section)
open(path, "w").write(content)
print("README.md patched")
PYEOF

# 4. Update test expectations
python3 - <<'PYEOF'
path = "services/mcp/tests/unit/tool-filtering.test.ts"
content = open(path).read()

# Update error-tracking test to include generated tool and add underscore variant
old_error = """        {
            features: ['error-tracking'],
            description: 'error tracking tools',
            expectedTools: ['list-errors', 'error-details', 'update-issue-status'],
        },"""
new_error = """        {
            features: ['error_tracking'],
            description: 'error tracking tools (underscore)',
            expectedTools: ['list-errors', 'error-details', 'update-issue-status', 'error-tracking-issues-list'],
        },
        {
            features: ['error-tracking'],
            description: 'error tracking tools (hyphen, normalized)',
            expectedTools: ['list-errors', 'error-details', 'update-issue-status', 'error-tracking-issues-list'],
        },"""
content = content.replace(old_error, new_error)

# Update llm-analytics test and add underscore variant
old_llm = """        {
            features: ['llm-analytics'],
            description: 'LLM analytics tools',
            expectedTools: ['get-llm-total-costs-for-project'],
        },"""
new_llm = """        {
            features: ['llm_analytics'],
            description: 'LLM analytics tools (underscore)',
            expectedTools: ['get-llm-total-costs-for-project'],
        },
        {
            features: ['llm-analytics'],
            description: 'LLM analytics tools (hyphen, normalized)',
            expectedTools: ['get-llm-total-costs-for-project'],
        },"""
content = content.replace(old_llm, new_llm)

open(path, "w").write(content)
print("test file patched")
PYEOF

echo "Patch applied successfully."
