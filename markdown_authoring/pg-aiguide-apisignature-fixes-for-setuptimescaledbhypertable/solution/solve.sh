#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pg-aiguide

# Idempotency guard
if grep -qF "**IMPORTANT**: If you used `tsdb.enable_columnstore=true` in Step 1, starting wi" "skills/setup-timescaledb-hypertables/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/setup-timescaledb-hypertables/SKILL.md b/skills/setup-timescaledb-hypertables/SKILL.md
@@ -184,13 +184,18 @@ CREATE TABLE ... (id BIGINT PRIMARY KEY, ...) WITH (tsdb.partition_column='id');
 
 **Option 3: No PK**: strict uniqueness is often not required for insert-heavy patterns.
 
-## Step 2: Compression Policy
+## Step 2: Compression Policy (Optional)
+
+**IMPORTANT**: If you used `tsdb.enable_columnstore=true` in Step 1, starting with TimescaleDB version 2.23 a columnstore policy is **automatically created** with `after => INTERVAL '7 days'`. You only need to call `add_columnstore_policy()` if you want to customize the `after` interval to something other than 7 days.
 
 Set `after` interval for when: data becomes mostly immutable (some updates/backfill OK) AND B-tree indexes aren't needed for queries (less common criterion).
 
 ```sql
--- Adjust 'after' based on update patterns
-CALL add_columnstore_policy('your_table_name', after => INTERVAL '1 day');
+-- In TimescaleDB 2.23 and later only needed if you want to override the default 7-day policy created by tsdb.enable_columnstore=true
+-- Remove the existing auto-created policy first:
+-- CALL remove_columnstore_policy('your_table_name');
+-- Then add custom policy:
+-- CALL add_columnstore_policy('your_table_name', after => INTERVAL '1 day');
 ```
 
 ## Step 3: Retention Policy
@@ -262,6 +267,7 @@ Set up refresh policies based on your data freshness requirements.
 
 ```sql
 SELECT add_continuous_aggregate_policy('your_table_hourly',
+    start_offset => NULL,
     end_offset => INTERVAL '15 minutes',
     schedule_interval => INTERVAL '15 minutes');
 ```
@@ -270,6 +276,7 @@ SELECT add_continuous_aggregate_policy('your_table_hourly',
 
 ```sql
 SELECT add_continuous_aggregate_policy('your_table_daily',
+    start_offset => NULL,
     end_offset => INTERVAL '1 hour',
     schedule_interval => INTERVAL '1 hour');
 ```
@@ -280,7 +287,7 @@ Use for high-volume systems where query accuracy on older data doesn't matter:
 ```sql
 -- the following aggregate can be stale for data older than 7 days
 -- SELECT add_continuous_aggregate_policy('aggregate_for_last_7_days',
---     start_offset => INTERVAL '7 days',    -- only refresh last 7 days
+--     start_offset => INTERVAL '7 days',    -- only refresh last 7 days (NULL = refresh all)
 --     end_offset => INTERVAL '15 minutes',
 --     schedule_interval => INTERVAL '15 minutes');
 ```
@@ -290,6 +297,7 @@ If the retention policy is commented out, comment out the start_offset as well.
 
 ```sql
 SELECT add_continuous_aggregate_policy('your_table_daily',
+    start_offset => NULL,    -- Use NULL to refresh all data, or set to retention period if enabled on raw data
 --  start_offset => INTERVAL '<retention period here>',    -- uncomment if retention policy is enabled on the raw data table
     end_offset => INTERVAL '1 hour',
     schedule_interval => INTERVAL '1 hour');
@@ -385,9 +393,8 @@ Only for query patterns where you ALWAYS filter by the space-partition column wi
 SELECT * FROM timescaledb_information.hypertables
 WHERE hypertable_name = 'your_table_name';
 
--- Check compression
-SELECT * FROM timescaledb_information.columnstore_settings
-WHERE hypertable_name LIKE 'your_table_name';
+-- Check compression settings
+SELECT * FROM hypertable_compression_stats('your_table_name');
 
 -- Check aggregates
 SELECT * FROM timescaledb_information.continuous_aggregates;
@@ -396,9 +403,14 @@ SELECT * FROM timescaledb_information.continuous_aggregates;
 SELECT * FROM timescaledb_information.jobs ORDER BY job_id;
 
 -- Monitor chunk information
-SELECT chunk_name, table_size, compressed_heap_size, compressed_index_size
+SELECT
+    chunk_name,
+    range_start,
+    range_end,
+    is_compressed
 FROM timescaledb_information.chunks
-WHERE hypertable_name = 'your_table_name';
+WHERE hypertable_name = 'your_table_name'
+ORDER BY range_start DESC;
 ```
 
 ## Performance Guidelines
@@ -435,19 +447,29 @@ WHERE hypertable_name = 'your_table_name';
 
 - `add_compression_policy()` → `add_columnstore_policy()`
 - `remove_compression_policy()` → `remove_columnstore_policy()`
-- `compress_chunk()` → `convert_to_columnstore()`
-- `decompress_chunk()` → `convert_to_rowstore()`
+- `compress_chunk()` → `convert_to_columnstore()` (use with `CALL`, not `SELECT`)
+- `decompress_chunk()` → `convert_to_rowstore()` (use with `CALL`, not `SELECT`)
 
-**Deprecated Views → New Views:**
+**Compression Stats (use functions, not views):**
 
-- `compression_settings` → `columnstore_settings`
-- `hypertable_compression_settings` → `hypertable_columnstore_settings`
-- `chunk_compression_settings` → `chunk_columnstore_settings`
+- Use function: `hypertable_compression_stats('table_name')`
+- Use function: `chunk_compression_stats('_timescaledb_internal._hyper_X_Y_chunk')`
+- Note: Views like `columnstore_settings` may not be available in all versions; use functions instead
 
-**Deprecated Stats Functions → New Stats Functions:**
+**Manual Compression Example:**
 
-- `hypertable_compression_stats()` → `hypertable_columnstore_stats()`
-- `chunk_compression_stats()` → `chunk_columnstore_stats()`
+```sql
+-- Compress a specific chunk
+CALL convert_to_columnstore('_timescaledb_internal._hyper_7_1_chunk');
+
+-- Check compression statistics
+SELECT
+    number_compressed_chunks,
+    pg_size_pretty(before_compression_total_bytes) as before_compression,
+    pg_size_pretty(after_compression_total_bytes) as after_compression,
+    ROUND(100.0 * (1 - after_compression_total_bytes::numeric / NULLIF(before_compression_total_bytes, 0)), 1) as compression_pct
+FROM hypertable_compression_stats('your_table_name');
+```
 
 ## Questions to Ask User
 
PATCH

echo "Gold patch applied."
