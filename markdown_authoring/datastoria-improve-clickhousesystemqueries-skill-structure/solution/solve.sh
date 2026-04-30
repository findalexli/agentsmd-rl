#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datastoria

# Idempotency guard
if grep -qF "2. **Load reference** \u2014 for `system.query_log`, call `skill_resource` to load `r" "resources/skills/clickhouse-system-queries/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/resources/skills/clickhouse-system-queries/SKILL.md b/resources/skills/clickhouse-system-queries/SKILL.md
@@ -1,6 +1,10 @@
 ---
 name: clickhouse-system-queries
-description: Dispatcher skill for ClickHouse system-table operational queries. Use table-specific references for concrete SQL patterns.
+description: >
+  Query ClickHouse system tables to inspect query logs, monitor cluster health,
+  check replication status, and analyze slow queries. Use when the user mentions
+  "system tables", "query_log", "ClickHouse monitoring", "cluster status",
+  "slow queries", or asks to diagnose ClickHouse operational issues.
 metadata:
   author: DataStoria
   disable-slash-command: true
@@ -21,37 +25,53 @@ Relationship to `sql-expert`:
 
 ## System Metrics and ProfileEvents
 
-- For metric-style columns in system tables, first confirm the actual column shape from schema/reference before writing predicates.
-- If the user already named an exact metric or event identifier, your first `explore_schema` call MUST pass that identifier in the `columns` list instead of loading the full table schema.
-- Treat exact flattened metric names such as `ProfileEvent_DistributedConnectionFailTry` as candidate columns unless the schema shows the table stores them in a map instead.
-- If `ProfileEvents` is a `Map`, access entries as `ProfileEvents['Name']`.
-- If the table exposes flattened columns, use `ProfileEvent_Name`.
-- Apply the same rule to other metric maps or flattened event columns: use the representation that exists in the target table, not the one you assume.
+- Confirm column shape from schema/reference before writing predicates.
+- If the user named an exact metric, pass it in the `columns` list via `explore_schema` instead of loading the full table schema.
+- If `ProfileEvents` is a `Map`, access entries as `ProfileEvents['Name']`. If flattened, use `ProfileEvent_Name`.
+
+Example — map vs flattened access:
+
+```sql
+-- Map access
+SELECT ProfileEvents['DistributedConnectionFailTry'] AS fails
+FROM system.query_log WHERE event_date = today();
+
+-- Flattened column access
+SELECT ProfileEvent_DistributedConnectionFailTry AS fails
+FROM system.query_log WHERE event_date = today();
+```
 
 ## Workflow
 
-1. Resolve target system table and intent.
-   - Identify whether the request is about query history (`system.query_log`) or other system tables.
-   - If user does not provide a new time window, inherit the most recent explicit time window/range from conversation.
-   - If no prior explicit time context exists, default to the last 60 minutes.
+1. **Resolve target** — identify system table and intent. Inherit the most recent time window from conversation, or default to last 60 minutes.
+
+2. **Load reference** — for `system.query_log`, call `skill_resource` to load `references/system-query-log.md` before writing any SQL. For unsupported tables, fall back to `sql-expert`.
+
+3. **Execute** — choose the right tool:
+   - `search_query_log` for standard ranked searches and filtered lookups
+   - `execute_sql` for visualization, time-bucketed aggregation, trends, or histograms
+
+   ```sql
+   -- search_query_log: standard lookup
+   -- finds top 10 slowest queries in the last hour
 
-2. Load the matching reference and follow it strictly.
-   - For `system.query_log`, you MUST call `skill_resource` to load `references/system-query-log.md` before writing, validating, or executing any SQL against `system.query_log`.
-   - For unsupported system tables, use `sql-expert` for safe fallback SQL generation.
+   -- execute_sql: time-bucketed visualization
+   SELECT toStartOfFiveMinutes(event_time) AS bucket,
+          count() AS queries,
+          avg(query_duration_ms) AS avg_ms
+   FROM system.query_log
+   WHERE event_date = today() AND event_time > now() - INTERVAL 1 HOUR
+   GROUP BY bucket ORDER BY bucket
+   ```
 
-3. Execute with `execute_sql`.
-   - For `system.query_log`, use `search_query_log` only for standard ranked searches and filtered lookups that return raw executions or grouped patterns.
-   - If the user wants visualization, time-bucketed aggregation, trends, histograms, or SQL grouped by hour/day/week/month, do NOT use `search_query_log`; generate SQL from `references/system-query-log.md` instead.
-   - Use `execute_sql` only when the request cannot be expressed by `search_query_log`, or when the task explicitly needs SQL output for visualization/chart rendering.
-   - Default to `LIMIT 50` unless the user specifies otherwise.
-   - Keep predicates aligned with intent and table semantics.
+   Default to `LIMIT 50` unless the user specifies otherwise.
 
-4. Summarize with concise findings and next actions.
+4. **Summarize** with concise findings and next actions.
 
 ## Guardrails
 
-- Always apply time bounds for log-like system tables.
-- Always use the table-specific reference when available.
-- Never generate `system.query_log` SQL until `references/system-query-log.md` is loaded in the current turn.
-- Never use `search_query_log` for chart-oriented `system.query_log` requests.
-- Never omit `LIMIT` in exploratory queries.
+- Always apply time bounds for log-like system tables
+- Always use the table-specific reference when available
+- Never generate `system.query_log` SQL until `references/system-query-log.md` is loaded in the current turn
+- Never use `search_query_log` for chart-oriented requests
+- Never omit `LIMIT` in exploratory queries
PATCH

echo "Gold patch applied."
