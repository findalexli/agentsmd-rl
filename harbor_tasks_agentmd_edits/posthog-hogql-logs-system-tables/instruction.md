# Add logs system tables to HogQL

## Problem

The logs product has two PostgreSQL-backed Django models (`LogsView` and `LogsAlertConfiguration`) that are not exposed as HogQL system tables. Other products (error tracking, experiments, surveys, etc.) already expose their configuration models through `system.*` tables, making them queryable via HogQL. Without these tables, users and agents cannot inspect log views or alert configurations through HogQL queries.

## Expected Behavior

Two new system tables should be available:
- `system.logs_views` — exposing saved log filter views (name, filters, pinned status, etc.)
- `system.logs_alerts` — exposing log alert configurations (thresholds, state, evaluation parameters, etc.)

Both tables should follow the same patterns as existing system tables (access scoping, field types, registration in `SystemTables`). The underlying Django models are `LogsView` (table: `logs_logsview`) and `LogsAlertConfiguration` (table: `logs_logsalertconfiguration`).

After adding the system table definitions, update the relevant skill documentation so that agents and users can discover and query these new tables. The project's query-examples skill reference docs should be updated to cover the new log tables.

## Files to Look At

- `posthog/hogql/database/schema/system.py` — where all PostgresTable system table definitions and the `SystemTables` registry live
- `products/posthog_ai/skills/query-examples/SKILL.md` — skill index listing all system model references
- `products/posthog_ai/skills/query-examples/references/guidelines.md` — system data table listing and model reference links
- `products/posthog_ai/skills/query-examples/references/` — where per-domain model reference docs live (see existing examples like `models-error-tracking.md`)
