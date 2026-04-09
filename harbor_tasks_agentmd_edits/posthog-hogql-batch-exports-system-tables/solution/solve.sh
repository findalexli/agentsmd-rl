#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'batch_exports.*PostgresTable' posthog/hogql/database/schema/system.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/posthog/hogql/database/schema/system.py b/posthog/hogql/database/schema/system.py
index 3a58961a3746..a3a5cc2f4913 100644
--- a/posthog/hogql/database/schema/system.py
+++ b/posthog/hogql/database/schema/system.py
@@ -31,6 +31,49 @@ def to_printed_hogql(self):
         return "ingestion_warnings"


+batch_export_backfills: PostgresTable = PostgresTable(
+    name="batch_export_backfills",
+    postgres_table_name="posthog_batchexportbackfill",
+    access_scope="batch_export",
+    fields={
+        "id": StringDatabaseField(name="id"),
+        "team_id": IntegerDatabaseField(name="team_id"),
+        "batch_export_id": StringDatabaseField(name="batch_export_id"),
+        "start_at": DateTimeDatabaseField(name="start_at", nullable=True),
+        "end_at": DateTimeDatabaseField(name="end_at", nullable=True),
+        "status": StringDatabaseField(name="status"),
+        "created_at": DateTimeDatabaseField(name="created_at"),
+        "finished_at": DateTimeDatabaseField(name="finished_at", nullable=True),
+        "last_updated_at": DateTimeDatabaseField(name="last_updated_at"),
+        "total_records_count": IntegerDatabaseField(name="total_records_count", nullable=True),
+    },
+)
+
+batch_exports: PostgresTable = PostgresTable(
+    name="batch_exports",
+    postgres_table_name="posthog_batchexport",
+    access_scope="batch_export",
+    fields={
+        "id": StringDatabaseField(name="id"),
+        "team_id": IntegerDatabaseField(name="team_id"),
+        "name": StringDatabaseField(name="name"),
+        "model": StringDatabaseField(name="model", nullable=True),
+        "interval": StringDatabaseField(name="interval"),
+        "_paused": BooleanDatabaseField(name="paused", hidden=True),
+        "paused": ExpressionField(name="paused", expr=ast.Call(name="toInt", args=[ast.Field(chain=["_paused"])])),
+        "_deleted": BooleanDatabaseField(name="deleted", hidden=True),
+        "deleted": ExpressionField(name="deleted", expr=ast.Call(name="toInt", args=[ast.Field(chain=["_deleted"])])),
+        "destination_id": StringDatabaseField(name="destination_id"),
+        "timezone": StringDatabaseField(name="timezone"),
+        "interval_offset": IntegerDatabaseField(name="interval_offset", nullable=True),
+        "created_at": DateTimeDatabaseField(name="created_at"),
+        "last_updated_at": DateTimeDatabaseField(name="last_updated_at"),
+        "last_paused_at": DateTimeDatabaseField(name="last_paused_at", nullable=True),
+        "start_at": DateTimeDatabaseField(name="start_at", nullable=True),
+        "end_at": DateTimeDatabaseField(name="end_at", nullable=True),
+    },
+)
+
 alerts: PostgresTable = PostgresTable(
     name="alerts",
     postgres_table_name="posthog_alertconfiguration",
@@ -596,6 +639,8 @@ class SystemTables(TableNode):
         "actions": TableNode(name="actions", table=actions),
         "alerts": TableNode(name="alerts", table=alerts),
         "annotations": TableNode(name="annotations", table=annotations),
+        "batch_export_backfills": TableNode(name="batch_export_backfills", table=batch_export_backfills),
+        "batch_exports": TableNode(name="batch_exports", table=batch_exports),
         "cohort_calculation_history": TableNode(name="cohort_calculation_history", table=cohort_calculation_history),
         "cohorts": TableNode(name="cohorts", table=cohorts),
         "dashboards": TableNode(name="dashboards", table=dashboards),

diff --git a/products/posthog_ai/skills/query-examples/SKILL.md b/products/posthog_ai/skills/query-examples/SKILL.md
index fe372112fb59..e297ecce2818 100644
--- a/products/posthog_ai/skills/query-examples/SKILL.md
+++ b/products/posthog_ai/skills/query-examples/SKILL.md
@@ -15,6 +15,7 @@ Schema reference for PostHog's core system models, organized by domain:
 - [Actions](./references/models-actions.md)
 - [Alerts](./references/models-alerts.md)
 - [Annotations](./references/models-annotations.md)
+- [Batch exports](./references/models-batch-exports.md)
 - [Early Access Features](./references/models-early-access-features.md)
 - [Cohorts & Persons](./references/models-cohorts.md)
 - [Dashboards, Tiles & Insights](./references/models-dashboards-insights.md)

diff --git a/products/posthog_ai/skills/query-examples/references/models-batch-exports.md b/products/posthog_ai/skills/query-examples/references/models-batch-exports.md
new file mode 100644
index 000000000000..52911293d6e0
--- /dev/null
+++ b/products/posthog_ai/skills/query-examples/references/models-batch-exports.md
@@ -0,0 +1,69 @@
+# Batch exports
+
+## BatchExport (`system.batch_exports`)
+
+Batch exports define recurring data export jobs that send events, persons, or sessions to external destinations.
+
+### Columns
+
+| Column            | Type              | Nullable | Description                                                                      |
+| ----------------- | ----------------- | -------- | -------------------------------------------------------------------------------- |
+| `id`              | uuid              | NOT NULL | Primary key                                                                      |
+| `team_id`         | integer           | NOT NULL | Team this export belongs to                                                      |
+| `name`            | text              | NOT NULL | Human-readable name                                                              |
+| `model`           | varchar(64)       | NULL     | Data model: `events`, `persons`, or `sessions`                                   |
+| `interval`        | varchar(64)       | NOT NULL | Schedule frequency: `hour`, `day`, `week`, `every 5 minutes`, `every 15 minutes` |
+| `paused`          | integer           | NOT NULL | Whether the export is paused (1 = paused, 0 = active)                            |
+| `deleted`         | integer           | NOT NULL | Soft-delete flag (1 = deleted, 0 = active)                                       |
+| `destination_id`  | uuid              | NOT NULL | FK to the destination configuration (not queryable as a system table)            |
+| `timezone`        | varchar(240)      | NOT NULL | IANA timezone for scheduling (e.g. `UTC`, `America/New_York`)                    |
+| `interval_offset` | integer           | NULL     | Offset in seconds from the default interval start time                           |
+| `created_at`      | timestamp with tz | NOT NULL | Creation timestamp                                                               |
+| `last_updated_at` | timestamp with tz | NOT NULL | Last modification timestamp                                                      |
+| `last_paused_at`  | timestamp with tz | NULL     | When the export was last paused                                                  |
+| `start_at`        | timestamp with tz | NULL     | Earliest time for scheduled runs                                                 |
+| `end_at`          | timestamp with tz | NULL     | Latest time for scheduled runs                                                   |
+
+### Key Relationships
+
+- Each batch export belongs to a **Team** (`team_id`)
+- Backfills reference this table via `system.batch_export_backfills.batch_export_id`
+
+### Important Notes
+
+- Filter with `deleted = 0` to exclude soft-deleted exports
+- Filter with `paused = 0` to find actively running exports
+- Destination details (type, connection config) are not in this table; use the `batch-export-get` MCP tool instead
+- Run history is not directly queryable via SQL; use the `batch-export-runs-list` MCP tool
+
+---
+
+## BatchExportBackfill (`system.batch_export_backfills`)
+
+Backfills are one-time historical data export jobs triggered for a batch export.
+
+### Columns
+
+| Column                | Type              | Nullable | Description                                         |
+| --------------------- | ----------------- | -------- | --------------------------------------------------- |
+| `id`                  | uuid              | NOT NULL | Primary key                                         |
+| `team_id`             | integer           | NOT NULL | Team this backfill belongs to                       |
+| `batch_export_id`     | uuid              | NOT NULL | FK to the parent batch export                       |
+| `start_at`            | timestamp with tz | NULL     | Start of the backfill time range                    |
+| `end_at`              | timestamp with tz | NULL     | End of the backfill time range                      |
+| `status`              | varchar(64)       | NOT NULL | Current status (see values below)                   |
+| `created_at`          | timestamp with tz | NOT NULL | Creation timestamp                                  |
+| `finished_at`         | timestamp with tz | NULL     | Completion timestamp                                |
+| `last_updated_at`     | timestamp with tz | NOT NULL | Last modification timestamp                         |
+| `total_records_count` | bigint            | NULL     | Total records exported (populated after completion) |
+
+### Key Relationships
+
+- Each backfill belongs to a **BatchExport** (`batch_export_id` -> `system.batch_exports.id`)
+- Each backfill belongs to a **Team** (`team_id`)
+
+### Important Notes
+
+- Status values: `Starting`, `Running`, `Completed`, `Failed`, `FailedRetryable`, `Cancelled`, `ContinuedAsNew`, `Terminated`, `TimedOut`
+- A `NULL` `start_at` means backfilling from the earliest available data
+- A `NULL` `end_at` means backfilling up to the current time
+
PATCH

echo "Patch applied successfully."
