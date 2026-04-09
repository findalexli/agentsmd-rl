#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'example-llm-traces-list.md' products/posthog_ai/skills/query-examples/SKILL.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/products/llm_analytics/skills/exploring-llm-traces/SKILL.md b/products/llm_analytics/skills/exploring-llm-traces/SKILL.md
index d54466d24670..c0f882d80661 100644
--- a/products/llm_analytics/skills/exploring-llm-traces/SKILL.md
+++ b/products/llm_analytics/skills/exploring-llm-traces/SKILL.md
@@ -1,10 +1,10 @@
 ---
 name: exploring-llm-traces
 description: >
-  How to query, inspect, and debug LLM traces using PostHog's MCP tools.
-  Use when the user asks to debug an AI agent trace, investigate LLM behavior,
-  inspect token usage or costs, find why an agent made a decision, or explore
-  AI/LLM observability data.
+    How to query, inspect, and debug LLM traces using PostHog's MCP tools.
+    Use when the user asks to debug an AI agent trace, investigate LLM behavior,
+    inspect token usage or costs, find why an agent made a decision, or explore
+    AI/LLM observability data.
 ---

 # Exploring LLM traces with MCP tools
@@ -138,6 +138,26 @@ When presenting findings, always include the relevant PostHog URL so the user ca

 ## Finding traces

+Use `posthog:query-llm-traces-list` to search and filter traces.
+
+**CRITICAL: Never assume event names, property names, or property values from training data.**
+Every project instruments different custom properties. Always call `posthog:read-data-schema` first
+to discover what properties and values actually exist in the project's data before constructing filters.
+
+### Discovering the schema first
+
+Before filtering traces, discover what's available:
+
+1. **Confirm AI events exist** — call `posthog:read-data-schema` with `kind: "events"` and look for `$ai_*` events
+2. **Find filterable properties** — call `posthog:read-data-schema` with `kind: "event_properties"` and `event_name: "$ai_generation"` (or another AI event) to see what properties are captured
+3. **Get actual values** — call `posthog:read-data-schema` with `kind: "event_property_values"`, `event_name: "$ai_generation"`, and `property_name: "$ai_model"` to see real model names in use
+
+Only then construct the `query-llm-traces-list` call with property filters.
+
+This is especially important for custom properties like `project_id`, `conversation_id`, `user_tier`, etc. — these vary per project and cannot be guessed.
+
+Do not confirm `$ai_*` properties, but confirm any other like `email` of a person.
+
 ### By filters

 ```json
@@ -152,10 +172,41 @@ posthog:query-llm-traces-list
 }
 ```

+Multiple filters are AND-ed together:
+
+```json
+posthog:query-llm-traces-list
+{
+  "dateRange": {"date_from": "-7d"},
+  "filterTestAccounts": true,
+  "properties": [
+    {"type": "event", "key": "$ai_provider", "value": "anthropic", "operator": "exact"},
+    {"type": "event", "key": "$ai_is_error", "value": ["true"], "operator": "exact"}
+  ]
+}
+```
+
+You can also filter by person properties (discover them via `read-data-schema` with `kind: "entity_properties"` and `entity: "person"`):
+
+```json
+posthog:query-llm-traces-list
+{
+  "dateRange": {"date_from": "-7d"},
+  "filterTestAccounts": true,
+  "properties": [
+    {"type": "person", "key": "email", "value": "@company.com", "operator": "icontains"}
+  ]
+}
+```
+
 ### By external identifiers

 Customers often store their own IDs as event or person properties.
-Use `read-data-schema` to discover available properties, then filter:
+Use `posthog:read-data-schema` to discover what custom properties exist, then filter:
+
+1. Call `posthog:read-data-schema` with `kind: "event_properties"` and `event_name: "$ai_trace"` to find custom properties
+2. Review the returned properties and their sample values
+3. Construct the filter using the discovered property key and a known value

 ```json
 posthog:query-llm-traces-list
@@ -169,6 +220,8 @@ posthog:query-llm-traces-list

 ### By content (SQL)

+When you need text search or complex joins that `query-llm-traces-list` can't express, use SQL:
+
 ```sql
 SELECT
     properties.$ai_trace_id AS trace_id,
@@ -183,6 +236,11 @@ ORDER BY timestamp DESC
 LIMIT 20
 ```

+For full SQL query patterns, see the `query-examples` skill:
+
+- Single trace retrieval: `example-llm-trace.md`
+- Traces list with aggregated metrics: `example-llm-traces-list.md`
+
 ## Parsing large trace results

 Trace tool results are JSON. When too large to read inline, Claude Code persists them to a file.
diff --git a/products/posthog_ai/skills/query-examples/SKILL.md b/products/posthog_ai/skills/query-examples/SKILL.md
index 5464704d82c9..1a9d28f62ee1 100644
--- a/products/posthog_ai/skills/query-examples/SKILL.md
+++ b/products/posthog_ai/skills/query-examples/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: query-examples
-description: 'HogQL query examples and reference material for PostHog data. Read when writing SQL queries to find patterns for analytics (trends, funnels, retention, lifecycle, paths, stickiness, web analytics, error tracking, logs, sessions, LLM traces) and system data (insights, dashboards, cohorts, feature flags, experiments, surveys, hog flows, data warehouse). Includes HogQL syntax differences, system model schemas, and available functions.'
+description: "HogQL query examples and reference material for PostHog data. Read when writing SQL queries to find patterns for analytics (trends, funnels, retention, lifecycle, paths, stickiness, web analytics, error tracking, logs, sessions, LLM traces) and system data (insights, dashboards, cohorts, feature flags, experiments, surveys, hog flows, data warehouse). Includes HogQL syntax differences, system model schemas, and available functions."
 ---

 # Querying data in PostHog
@@ -49,6 +49,7 @@ Use the examples below to create optimized analytical queries.
 - [Lifecycle (unique users by pageviews)](./references/example-lifecycle.md)
 - [Stickiness (counted by pageviews from unique users, defined by at least one event for the interval, non-cumulative)](./references/example-stickiness.md)
 - [LLM trace (generations, spans, embeddings, human feedback, captured AI metrics)](./references/example-llm-trace.md)
+- [LLM traces list (searching and listing traces with property filters, two-phase query)](./references/example-llm-traces-list.md)
 - [Web path stats (paths, visitors, views, bounce rate)](./references/example-web-path-stats.md)
 - [Web traffic channels (direct, organic search, etc)](./references/example-web-traffic-channels.md)
 - [Web views by devices](./references/example-web-traffic-by-device-type.md)
diff --git a/products/posthog_ai/skills/query-examples/references/example-llm-trace.md b/products/posthog_ai/skills/query-examples/references/example-llm-trace.md
deleted file mode 100644
index c74cb782e322..000000000000
--- a/products/posthog_ai/skills/query-examples/references/example-llm-trace.md
+++ /dev/null
@@ -1,34 +0,0 @@
-# LLM Trace query
-
-This query might return a very large blob of JSON data. You should either only include data you need in case it's minimal or dump the results to a file and use bash commands to explore it.
-This query must always have time ranges set. You can calculate the time range as -30 to +30 minutes from the source event.
-The typical order of event capture for a trace is: $ai_span -> $ai_generation/$ai_embedding -> $ai_trace.
-Explore `$ai\_\*`-prefixed properties to find data related to traces, generations, embeddings, spans, feedback, and metric.
-Key properties of the $ai_generation event: $ai_input and $ai_output_choices.
-
-**IMPORTANT:** The `$ai_input`, `$ai_input_state`, and `$ai_output_state` properties can be extremely large (containing full conversation histories, system prompts, or application state). When your query selects these properties, you MUST dump the results to a file and use bash commands to explore the output. Never output them directly into the conversation.
-
-```sql
-SELECT
-    properties.$ai_trace_id AS id,
-    any(properties.$ai_session_id) AS ai_session_id,
-    min(timestamp) AS first_timestamp,
-    tuple(argMin(person.id, timestamp), ifNull(nullIf(argMinIf(distinct_id, timestamp, event = '$ai_trace'), ''), argMin(distinct_id, timestamp)), argMin(person.created_at, timestamp), argMin(person.properties, timestamp)) AS first_person,
-    round(if(and(equals(countIf(and(greater(toFloat(properties.$ai_latency), 0), notEquals(event, '$ai_generation'))), 0), greater(countIf(and(greater(toFloat(properties.$ai_latency), 0), equals(event, '$ai_generation'))), 0)), sumIf(toFloat(properties.$ai_latency), and(equals(event, '$ai_generation'), greater(toFloat(properties.$ai_latency), 0))), sumIf(toFloat(properties.$ai_latency), or(equals(properties.$ai_parent_id, NULL), equals(toString(properties.$ai_parent_id), toString(properties.$ai_trace_id))))), 2) AS total_latency,
-    sumIf(toFloat(properties.$ai_input_tokens), in(event, tuple('$ai_generation', '$ai_embedding'))) AS input_tokens,
-    sumIf(toFloat(properties.$ai_output_tokens), in(event, tuple('$ai_generation', '$ai_embedding'))) AS output_tokens,
-    round(sumIf(toFloat(properties.$ai_input_cost_usd), in(event, tuple('$ai_generation', '$ai_embedding'))), 4) AS input_cost,
-    round(sumIf(toFloat(properties.$ai_output_cost_usd), in(event, tuple('$ai_generation', '$ai_embedding'))), 4) AS output_cost,
-    round(sumIf(toFloat(properties.$ai_total_cost_usd), in(event, tuple('$ai_generation', '$ai_embedding'))), 4) AS total_cost,
-    arrayDistinct(arraySort(x -> x.3, groupArrayIf(tuple(uuid, event, timestamp, properties), notEquals(event, '$ai_trace')))) AS events,
-    argMinIf(properties.$ai_input_state, timestamp, equals(event, '$ai_trace')) AS input_state,
-    argMinIf(properties.$ai_output_state, timestamp, equals(event, '$ai_trace')) AS output_state,
-    ifNull(argMinIf(ifNull(properties.$ai_span_name, properties.$ai_trace_name), timestamp, equals(event, '$ai_trace')), argMin(ifNull(properties.$ai_span_name, properties.$ai_trace_name), timestamp)) AS trace_name
-FROM
-    events
-WHERE
-    and(in(event, tuple('$ai_span', '$ai_generation', '$ai_embedding', '$ai_metric', '$ai_feedback', '$ai_trace')), and(greaterOrEquals(events.timestamp, assumeNotNull(toDateTime('2026-01-27 23:45:41'))), lessOrEquals(events.timestamp, assumeNotNull(toDateTime('2026-01-28 00:15:41'))), equals(properties.$ai_trace_id, '79955c94-7453-488f-a84a-eabb6f084e4c')))
-GROUP BY
-    properties.$ai_trace_id
-LIMIT 1
-```
diff --git a/products/posthog_ai/skills/query-examples/references/example-llm-trace.md.j2 b/products/posthog_ai/skills/query-examples/references/example-llm-trace.md.j2
new file mode 100644
index 000000000000..bdc6066ee580
--- /dev/null
+++ b/products/posthog_ai/skills/query-examples/references/example-llm-trace.md.j2
@@ -0,0 +1,13 @@
+# LLM Trace query
+
+This query might return a very large blob of JSON data. You should either only include data you need in case it's minimal or dump the results to a file and use bash commands to explore it.
+This query must always have time ranges set. You can calculate the time range as -30 to +30 minutes from the source event.
+The typical order of event capture for a trace is: $ai_span -> $ai_generation/$ai_embedding -> $ai_trace.
+Explore `$ai\_\*`-prefixed properties to find data related to traces, generations, embeddings, spans, feedback, and metric.
+Key properties of the $ai_generation event: $ai_input and $ai_output_choices.
+
+**IMPORTANT:** The `$ai_input`, `$ai_input_state`, and `$ai_output_state` properties can be extremely large (containing full conversation histories, system prompts, or application state). When your query selects these properties, you MUST dump the results to a file and use bash commands to explore the output. Never output them directly into the conversation.
+
+```sql
+{{ render_hogql_example({"kind": "TraceQuery", "traceId": "79955c94-7453-488f-a84a-eabb6f084e4c", "dateRange": {"date_from": "2025-12-09T23:45:41", "date_to": "2025-12-10T00:15:41", "explicitDate": true}}) }}
+```
diff --git a/products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md b/products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md
new file mode 100644
index 000000000000..4554b8d90a49
--- /dev/null
+++ b/products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md
@@ -0,0 +1,89 @@
+# LLM Traces list query
+
+List multiple LLM traces with aggregated latency, token usage, costs, and error counts.
+This is a two-phase query for performance: first find matching trace IDs, then fetch full trace data.
+Time ranges are always required. Results can be large — dump to a file if needed.
+
+This query intentionally omits large content fields (`$ai_input`, `$ai_output_choices`, `$ai_input_state`, `$ai_output_state`).
+Use the [single trace query](./example-llm-trace.md) to retrieve those for a specific trace.
+
+## Phase 1 — Find trace IDs
+
+Use this subquery to find trace IDs matching your criteria. Add property filters here for efficiency.
+
+```sql
+SELECT
+    properties.$ai_trace_id AS trace_id,
+    min(timestamp) AS first_ts,
+    max(timestamp) AS last_ts
+FROM events
+WHERE
+    event IN ('$ai_span', '$ai_generation', '$ai_embedding', '$ai_metric', '$ai_feedback', '$ai_trace')
+    AND isNotNull(properties.$ai_trace_id)
+    AND properties.$ai_trace_id != ''
+    AND timestamp >= toDateTime('2026-03-01 00:00:00')
+    AND timestamp <= toDateTime('2026-04-01 00:00:00')
+    -- Add property filters here, e.g.:
+    -- AND properties.$ai_model = 'gpt-4o'
+    -- AND properties.$ai_is_error = 'true'
+GROUP BY trace_id
+ORDER BY min(timestamp) DESC
+LIMIT 20
+```
+
+## Phase 2 — Fetch trace data
+
+Use the trace IDs from phase 1 to fetch aggregated metrics. Replace the `IN (...)` clause with the IDs found above.
+
+```sql
+SELECT
+    properties.$ai_trace_id AS id,
+    any(properties.$ai_session_id) AS ai_session_id,
+    min(timestamp) AS first_timestamp,
+    ifNull(
+        nullIf(argMinIf(distinct_id, timestamp, event = '$ai_trace'), ''),
+        argMin(distinct_id, timestamp)
+    ) AS first_distinct_id,
+    round(
+        CASE
+            WHEN countIf(toFloat(properties.$ai_latency) > 0 AND event != '$ai_generation') = 0
+                 AND countIf(toFloat(properties.$ai_latency) > 0 AND event = '$ai_generation') > 0
+            THEN sumIf(toFloat(properties.$ai_latency),
+                       event = '$ai_generation' AND toFloat(properties.$ai_latency) > 0)
+            ELSE sumIf(toFloat(properties.$ai_latency),
+                       properties.$ai_parent_id IS NULL
+                       OR toString(properties.$ai_parent_id) = toString(properties.$ai_trace_id))
+        END, 2
+    ) AS total_latency,
+    sumIf(toFloat(properties.$ai_input_tokens),
+          event IN ('$ai_generation', '$ai_embedding')) AS input_tokens,
+    sumIf(toFloat(properties.$ai_output_tokens),
+          event IN ('$ai_generation', '$ai_embedding')) AS output_tokens,
+    round(sumIf(toFloat(properties.$ai_input_cost_usd),
+          event IN ('$ai_generation', '$ai_embedding')), 10) AS input_cost,
+    round(sumIf(toFloat(properties.$ai_output_cost_usd),
+          event IN ('$ai_generation', '$ai_embedding')), 10) AS output_cost,
+    round(sumIf(toFloat(properties.$ai_total_cost_usd),
+          event IN ('$ai_generation', '$ai_embedding')), 10) AS total_cost,
+    ifNull(
+        argMinIf(
+            ifNull(properties.$ai_span_name, properties.$ai_trace_name),
+            timestamp, event = '$ai_trace'
+        ),
+        argMin(
+            ifNull(properties.$ai_span_name, properties.$ai_trace_name),
+            timestamp
+        )
+    ) AS trace_name,
+    countIf(
+        isNotNull(properties.$ai_error) OR properties.$ai_is_error = 'true'
+    ) AS error_count
+FROM events
+WHERE
+    event IN ('$ai_span', '$ai_generation', '$ai_embedding', '$ai_metric', '$ai_feedback', '$ai_trace')
+    AND timestamp >= toDateTime('2026-03-01 00:00:00')
+    AND timestamp <= toDateTime('2026-04-01 00:00:00')
+    AND properties.$ai_trace_id IN ('trace-id-1', 'trace-id-2')
+GROUP BY properties.$ai_trace_id
+ORDER BY first_timestamp DESC
+```

PATCH

echo "Patch applied successfully."
