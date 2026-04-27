#!/usr/bin/env bash
set -euo pipefail

cd /workspace/byterover-cli

# Idempotency guard
if grep -qF "**Overview:** Inspect past query and curate operations. Use `brv query-log view`" "src/server/templates/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/server/templates/skill/SKILL.md b/src/server/templates/skill/SKILL.md
@@ -77,28 +77,6 @@ brv curate "Auth uses JWT with 24h expiry. Tokens stored in httpOnly cookies via
 brv curate "Authentication middleware details" -f src/middleware/auth.ts
 ```
 
-**View curate history:** to check past curations
-- Show recent entries (last 10)
-```bash
-brv curate view
-```
-- Full detail for a specific entry: all files and operations performed (logId is printed by `brv curate` on completion, e.g. `cur-1739700001000`)
-```bash
-brv curate view cur-1739700001000
-```
-- List entries with file operations visible (no logId needed)
-```bash
-brv curate view detail
-```
-- Filter by time and status
-```bash
-brv curate view --since 1h --status completed
-```
-- For all filter options
-```bash
-brv curate view --help
-```
-
 ### 4. Review Pending Changes
 **Overview:** After a curate operation, some changes may require human review before being applied. Use `brv review` to list, approve, or reject pending operations.
 
@@ -473,6 +451,85 @@ Write Targets:
 Swarm is operational (5/5 providers configured).
 ```
 
+### 11. Query and Curate History
+**Overview:** Inspect past query and curate operations. Use `brv query-log view` to review query history, `brv curate view` to review curate history, and `brv query-log summary` to see aggregated recall metrics. Supports filtering by time, status, tier, and detailed per-operation output.
+
+**Use this skill when:**
+- You want to review what was queried or curated previously
+- You need to inspect a specific operation by logId
+- You want to filter history by time window or completion status
+- You want to collect data for analysis or debugging
+- You want to know what knowledge was added, updated, or deleted over time
+- You want aggregated metrics on query recall, cache hit rate, or knowledge gaps
+
+**Do NOT use this skill when:**
+- You want to run a new query — use `brv query` instead
+- You want to curate new knowledge — use `brv curate` instead
+
+**View curate history:** to check past curations
+- Show recent entries (last 10)
+```bash
+brv curate view
+```
+- Full detail for a specific entry: all files and operations performed (logId is printed by `brv curate` on completion, e.g. `cur-1739700001000`)
+```bash
+brv curate view cur-1739700001000
+```
+- List entries with file operations visible (no logId needed)
+```bash
+brv curate view --detail
+```
+- Filter by time and status
+```bash
+brv curate view --since 1h --status completed --limit 1000
+```
+- For all filter options
+```bash
+brv curate view --help
+```
+
+**View query history:** to check past queries
+- Show recent entries (last 10)
+```bash
+brv query-log view
+```
+- Full detail for a specific entry: matched docs and search metadata (logId is printed by `brv query` on completion, e.g. `qry-1739700001000`)
+```bash
+brv query-log view qry-1739700001000
+```
+- List entries with matched docs visible (no logId needed)
+```bash
+brv query-log view --detail
+```
+- Filter by time, status, or resolution tier (0=exact cache, 1=fuzzy cache, 2=direct search, 3=optimized LLM, 4=full agentic)
+```bash
+brv query-log view --since 1h --status completed --limit 1000
+brv query-log view --tier 0 --tier 1
+```
+- For all filter options
+```bash
+brv query-log view --help
+```
+
+**View query recall metrics:** to see aggregated stats across recent queries
+- Summary for the last 24 hours (default)
+```bash
+brv query-log summary
+```
+- Summary for a specific time window
+```bash
+brv query-log summary --last 7d
+brv query-log summary --since 2026-04-01 --before 2026-04-03
+```
+- Narrative format (human-readable prose report)
+```bash
+brv query-log summary --format narrative
+```
+- For all options
+```bash
+brv query-log summary --help
+```
+
 ## Data Handling
 
 **Storage**: All knowledge is stored as Markdown files in `.brv/context-tree/` within the project directory. Files are human-readable and version-controllable.
PATCH

echo "Gold patch applied."
