# feat(hogql): add batch exports system tables

## Problem

Batch exports and backfills are not queryable via HogQL system tables, making it harder for the AI agent and users to introspect export configuration and backfill status through SQL.

## Required Changes

Add `system.batch_exports` and `system.batch_export_backfills` as HogQL system tables backed by PostgreSQL via the existing `PostgresTable` pattern. Both tables should be scoped with `access_scope="batch_export"` for RBAC filtering.

### Code Changes

1. **posthog/hogql/database/schema/system.py**:
   - Add `batch_export_backfills` PostgresTable definition with fields: `id`, `team_id`, `batch_export_id`, `start_at`, `end_at`, `status`, `created_at`, `finished_at`, `last_updated_at`, `total_records_count`
   - Add `batch_exports` PostgresTable definition with fields: `id`, `team_id`, `name`, `model`, `interval`, `paused`, `deleted`, `destination_id`, `timezone`, `interval_offset`, `created_at`, `last_updated_at`, `last_paused_at`, `start_at`, `end_at`
   - Note: `paused` and `deleted` should use `ExpressionField` with `toInt` conversion from hidden `_paused` and `_deleted` boolean fields
   - Register both tables in the `SystemTables` class dictionary

2. **products/posthog_ai/skills/query-examples/SKILL.md**:
   - Add a link to the new batch exports reference documentation in the "Data Schema" section

3. **products/posthog_ai/skills/query-examples/references/models-batch-exports.md** (create this file):
   - Document the `system.batch_exports` table columns and relationships
   - Document the `system.batch_export_backfills` table columns and relationships
   - Include column types, nullability, and important notes about usage

## Files to Look At

- `posthog/hogql/database/schema/system.py` — where system tables are defined
- `products/posthog_ai/skills/query-examples/SKILL.md` — skill documentation index
- `products/posthog_ai/skills/query-examples/references/` — reference docs for system models
- Look at existing system table definitions (like `alerts`, `cohorts`) in system.py for the pattern to follow
