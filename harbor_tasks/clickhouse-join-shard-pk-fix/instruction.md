# Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem

JOIN queries with shard-by-primary-key optimization return incorrect results (0 rows) when the query condition cache is enabled. This happens because the optimization logic makes an incorrect assumption about how data parts are indexed.

## Context

When executing a distributed JOIN query, ClickHouse uses the `optimizeJoinByShards` optimization to distribute parts across worker nodes based on primary key ranges. This optimization uses `part_index_in_query` values to track which part belongs to which query source.

However, when the query condition cache is active, it can filter out parts that don't match cached conditions via `filterPartsByQueryConditionCache()`. This removes parts from the result set, but the remaining parts retain their original indices - creating gaps in the sequence.

The distribution logic assumes contiguous indices starting from 0 to assign parts back to their sources. When indices have gaps, parts get assigned to wrong sources or dropped entirely, causing queries to return empty results.

## Files to Modify

- `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp`

## Specific Location

Focus on the `apply()` function in the `JoinsAndSourcesWithCommonPrimaryKeyPrefix` struct. Look for the loop that iterates over `analysis_result->parts_with_ranges` and assigns `part_index_in_query` values.

## What Needs to Change

The loop that processes parts needs to ensure that `part_index_in_query` values are contiguous starting from the current offset (`added_parts`), regardless of any gaps that may exist in the source indices.

## Expected Behavior

After the fix, JOIN queries with:
- `query_plan_join_shard_by_pk_ranges = 1` (shard-by-PK optimization enabled)
- `use_query_condition_cache = 1` (query condition cache enabled)

Should return correct results instead of 0 rows.

## Testing

The repository includes stateless tests at `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` that demonstrate the bug. The test:
1. Creates two tables with statistics-based join optimization
2. Populates the query condition cache with a false condition
3. Inserts new matching data
4. Verifies the JOIN returns the correct row (not 0 rows)

## Hints

- The issue is in how `part_index_in_query` is computed inside the loop
- Currently it may be adding an offset to the original index, but should be assigning a new contiguous index
- Look for where `all_parts.back().part_index_in_query` is assigned
- Consider what happens when some parts are filtered out before this loop runs
