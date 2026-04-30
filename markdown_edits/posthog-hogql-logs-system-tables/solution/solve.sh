#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'logs_views: PostgresTable' posthog/hogql/database/schema/system.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/posthog/hogql/database/schema/system.py b/posthog/hogql/database/schema/system.py
index 4bd3ab8d0480..7a9290abfa4b 100644
--- a/posthog/hogql/database/schema/system.py
+++ b/posthog/hogql/database/schema/system.py
@@ -631,6 +631,52 @@ def to_printed_hogql(self):
     },
 )

+logs_views: PostgresTable = PostgresTable(
+    name="logs_views",
+    postgres_table_name="logs_logsview",
+    access_scope="logs",
+    fields={
+        "id": StringDatabaseField(name="id"),
+        "team_id": IntegerDatabaseField(name="team_id"),
+        "short_id": StringDatabaseField(name="short_id"),
+        "name": StringDatabaseField(name="name"),
+        "filters": StringJSONDatabaseField(name="filters"),
+        "_pinned": BooleanDatabaseField(name="pinned", hidden=True),
+        "pinned": ExpressionField(name="pinned", expr=ast.Call(name="toInt", args=[ast.Field(chain=["_pinned"])])),
+        "created_at": DateTimeDatabaseField(name="created_at"),
+        "updated_at": DateTimeDatabaseField(name="updated_at"),
+    },
+)
+
+logs_alerts: PostgresTable = PostgresTable(
+    name="logs_alerts",
+    postgres_table_name="logs_logsalertconfiguration",
+    access_scope="logs",
+    fields={
+        "id": StringDatabaseField(name="id"),
+        "team_id": IntegerDatabaseField(name="team_id"),
+        "name": StringDatabaseField(name="name"),
+        "_enabled": BooleanDatabaseField(name="enabled", hidden=True),
+        "enabled": ExpressionField(name="enabled", expr=ast.Call(name="toInt", args=[ast.Field(chain=["_enabled"])])),
+        "filters": StringJSONDatabaseField(name="filters"),
+        "threshold_count": IntegerDatabaseField(name="threshold_count"),
+        "threshold_operator": StringDatabaseField(name="threshold_operator"),
+        "window_minutes": IntegerDatabaseField(name="window_minutes"),
+        "check_interval_minutes": IntegerDatabaseField(name="check_interval_minutes"),
+        "state": StringDatabaseField(name="state"),
+        "evaluation_periods": IntegerDatabaseField(name="evaluation_periods"),
+        "datapoints_to_alarm": IntegerDatabaseField(name="datapoints_to_alarm"),
+        "cooldown_minutes": IntegerDatabaseField(name="cooldown_minutes"),
+        "snooze_until": DateTimeDatabaseField(name="snooze_until", nullable=True),
+        "next_check_at": DateTimeDatabaseField(name="next_check_at", nullable=True),
+        "last_notified_at": DateTimeDatabaseField(name="last_notified_at", nullable=True),
+        "last_checked_at": DateTimeDatabaseField(name="last_checked_at", nullable=True),
+        "consecutive_failures": IntegerDatabaseField(name="consecutive_failures"),
+        "created_at": DateTimeDatabaseField(name="created_at"),
+        "updated_at": DateTimeDatabaseField(name="updated_at"),
+    },
+)
+
 early_access_features: PostgresTable = PostgresTable(
     name="early_access_features",
     postgres_table_name="posthog_earlyaccessfeature",
@@ -684,6 +730,8 @@ class SystemTables(TableNode):
         "ingestion_warnings": TableNode(name="ingestion_warnings", table=IngestionWarningsTable()),
         "integrations": TableNode(name="integrations", table=integrations),
         "insight_variables": TableNode(name="insight_variables", table=insight_variables),
+        "logs_alerts": TableNode(name="logs_alerts", table=logs_alerts),
+        "logs_views": TableNode(name="logs_views", table=logs_views),
         "insights": TableNode(name="insights", table=insights),
         "notebooks": TableNode(name="notebooks", table=notebooks),
         "source_schemas": TableNode(name="source_schemas", table=source_schemas),
diff --git a/products/posthog_ai/skills/query-examples/SKILL.md b/products/posthog_ai/skills/query-examples/SKILL.md
index 62d0f800a260..0acafd0bb77d 100644
--- a/products/posthog_ai/skills/query-examples/SKILL.md
+++ b/products/posthog_ai/skills/query-examples/SKILL.md
@@ -26,6 +26,7 @@ Schema reference for PostHog's core system models, organized by domain:
 - [Hog Flows](./references/models-hog-flows.md)
 - [Hog Functions](./references/models-hog-functions.md)
 - [Integrations](./references/models-integrations.md)
+- [Logs](./references/models-logs.md)
 - [Notebooks](./references/models-notebooks.md)
 - [Surveys](./references/models-surveys.md)
 - [SQL Variables](./references/models-variables.md)
diff --git a/products/posthog_ai/skills/query-examples/references/guidelines.md b/products/posthog_ai/skills/query-examples/references/guidelines.md
index 149cbbc30f36..b4e07c0cbd80 100644
--- a/products/posthog_ai/skills/query-examples/references/guidelines.md
+++ b/products/posthog_ai/skills/query-examples/references/guidelines.md
@@ -36,6 +36,8 @@ Table | Description
 `system.ingestion_warnings` | Data ingestion issues
 `system.insight_variables` | SQL, dashboard, and insight variables for dynamic query filtering
 `system.insights` | Visual and textual representations of aggregated data
+`system.logs_alerts` | Log alert configurations and their states
+`system.logs_views` | Saved log filter views
 `system.notebooks` | Collaborative documents with embedded insights
 `system.surveys` | Questionnaires and feedback forms
 `system.teams` | Team/project settings
@@ -55,6 +57,7 @@ Schema reference for PostHog's core system models, organized by domain:
 - [Dashboards, Tiles & Insights](references/models-dashboards-insights.md)
 - [Data Warehouse](references/models-data-warehouse.md)
 - [Error Tracking](references/models-error-tracking.md)
+- [Logs](references/models-logs.md)
 - [Flags & Experiments](references/models-flags-experiments.md)
 - [Notebooks](references/models-notebooks.md)
 - [Surveys](references/models-surveys.md)
diff --git a/products/posthog_ai/skills/query-examples/references/models-logs.md b/products/posthog_ai/skills/query-examples/references/models-logs.md
new file mode 100644
index 000000000000..fc6f76f841ee
--- /dev/null
+++ b/products/posthog_ai/skills/query-examples/references/models-logs.md
@@ -0,0 +1,140 @@
+# Logs
+
+## LogsView (`system.logs_views`)
+
+Saved log views — named filter configurations that users create to quickly access frequently-used log queries.
+
+### Columns
+
+| Column       | Type              | Nullable | Description                                                           |
+| ------------ | ----------------- | -------- | --------------------------------------------------------------------- |
+| `id`         | uuid              | NOT NULL | Primary key                                                           |
+| `team_id`    | integer           | NOT NULL | Team this view belongs to                                             |
+| `short_id`   | varchar(12)       | NOT NULL | URL-friendly short identifier                                         |
+| `name`       | varchar(400)      | NOT NULL | Display name                                                          |
+| `filters`    | jsonb             | NOT NULL | Saved filter criteria (severity levels, service names, filter groups) |
+| `pinned`     | boolean           | NOT NULL | Whether the view is pinned for quick access                           |
+| `created_at` | timestamp with tz | NOT NULL | Creation timestamp                                                    |
+| `updated_at` | timestamp with tz | NOT NULL | Last update timestamp                                                 |
+
+### Key Relationships
+
+- Views belong to a **Team** (`team_id`)
+- The `filters` field stores the same filter structure used by the logs viewer UI
+
+### Important Notes
+
+- The `short_id` is auto-generated and unique per team
+- `filters` typically contains `severityLevels`, `serviceNames`, and `filterGroup` keys
+
+---
+
+## LogsAlertConfiguration (`system.logs_alerts`)
+
+Alerts that monitor log volume and notify users when thresholds are breached. Uses an N-of-M evaluation model (similar to AWS CloudWatch alarms).
+
+### Columns
+
+| Column                   | Type              | Nullable | Description                                                         |
+| ------------------------ | ----------------- | -------- | ------------------------------------------------------------------- |
+| `id`                     | uuid              | NOT NULL | Primary key                                                         |
+| `team_id`                | integer           | NOT NULL | Team this alert belongs to                                          |
+| `name`                   | varchar(255)      | NOT NULL | Alert name                                                          |
+| `enabled`                | boolean           | NOT NULL | Whether the alert is actively evaluated                             |
+| `filters`                | jsonb             | NOT NULL | Log filter criteria (severity levels, service names, filter groups) |
+| `threshold_count`        | integer           | NOT NULL | Number of log entries that triggers the alert                       |
+| `threshold_operator`     | varchar(10)       | NOT NULL | `above` or `below`                                                  |
+| `window_minutes`         | integer           | NOT NULL | Time window in minutes to evaluate                                  |
+| `check_interval_minutes` | integer           | NOT NULL | How often the alert is checked (minutes)                            |
+| `state`                  | varchar(20)       | NOT NULL | Current alert state (see State Values below)                        |
+| `evaluation_periods`     | integer           | NOT NULL | Number of periods in the evaluation window (M in N-of-M)            |
+| `datapoints_to_alarm`    | integer           | NOT NULL | Breaches needed to fire (N in N-of-M)                               |
+| `cooldown_minutes`       | integer           | NOT NULL | Minutes to wait after firing before re-evaluating                   |
+| `snooze_until`           | timestamp with tz | NULL     | Snooze expiry (UTC)                                                 |
+| `next_check_at`          | timestamp with tz | NULL     | When the next evaluation is scheduled                               |
+| `last_notified_at`       | timestamp with tz | NULL     | When subscribers were last notified                                 |
+| `last_checked_at`        | timestamp with tz | NULL     | When the alert was last evaluated                                   |
+| `consecutive_failures`   | integer           | NOT NULL | Number of consecutive evaluation failures                           |
+| `created_at`             | timestamp with tz | NOT NULL | Creation timestamp                                                  |
+| `updated_at`             | timestamp with tz | NOT NULL | Last update timestamp                                               |
+
+### State Values
+
+| State             | Description                                           |
+| ----------------- | ----------------------------------------------------- |
+| `not_firing`      | Alert is within normal thresholds                     |
+| `firing`          | Threshold breached, notifications sent                |
+| `pending_resolve` | Was firing, waiting for confirmation that it resolved |
+| `errored`         | Evaluation failed                                     |
+| `snoozed`         | Temporarily silenced until `snooze_until`             |
+
+### Key Relationships
+
+- Alerts belong to a **Team** (`team_id`)
+- Alert checks are stored in `LogsAlertCheck` (not exposed as a system table)
+
+### Important Notes
+
+- The N-of-M model: alert fires when `datapoints_to_alarm` (N) out of the last `evaluation_periods` (M) checks breach the threshold
+- `datapoints_to_alarm` must be <= `evaluation_periods`
+- Disabled alerts automatically have their state set to `not_firing`
+
+---
+
+## Common Query Patterns
+
+**List all saved log views:**
+
+```sql
+SELECT id, name, short_id, pinned, created_at
+FROM system.logs_views
+ORDER BY created_at DESC
+LIMIT 20
+```
+
+**Find pinned log views:**
+
+```sql
+SELECT id, name, short_id
+FROM system.logs_views
+WHERE pinned
+ORDER BY name
+```
+
+**List active log alerts:**
+
+```sql
+SELECT id, name, state, threshold_count, threshold_operator, window_minutes
+FROM system.logs_alerts
+WHERE enabled
+  AND state != 'snoozed'
+ORDER BY created_at DESC
+```
+
+**Find firing log alerts:**
+
+```sql
+SELECT id, name, state, last_checked_at, last_notified_at
+FROM system.logs_alerts
+WHERE state = 'firing'
+ORDER BY last_notified_at DESC
+```
+
+**Count log alerts by state:**
+
+```sql
+SELECT state, count() AS count
+FROM system.logs_alerts
+WHERE enabled
+GROUP BY state
+ORDER BY count DESC
+```
+
+**Find errored or failing log alerts:**
+
+```sql
+SELECT id, name, state, consecutive_failures, last_checked_at
+FROM system.logs_alerts
+WHERE state = 'errored' OR consecutive_failures > 0
+ORDER BY consecutive_failures DESC
+```

PATCH

echo "Patch applied successfully."
