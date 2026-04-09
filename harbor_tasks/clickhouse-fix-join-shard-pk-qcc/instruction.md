# Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem Description

There is a bug in the JOIN query optimization that combines shard-by-primary-key optimization with the query condition cache. This combination can produce wrong results (returning 0 rows when data should be returned).

## Location

The bug is in the file:
```
src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp
```

Specifically, in the `apply()` function within the `JoinsAndSourcesWithCommonPrimaryKeyPrefix` struct.

## The Bug

When processing parts for JOIN with shard-by-PK optimization, the code iterates over `analysis_result->parts_with_ranges` and assigns `part_index_in_query` values by adding `added_parts` to the existing index:

```cpp
for (const auto & part : analysis_result->parts_with_ranges)
{
    all_parts.push_back(part);
    all_parts.back().part_index_in_query += added_parts;
}
```

The problem is that `filterPartsByQueryConditionCache` may drop parts from `selectRangesToRead()`, leaving **non-contiguous** `part_index_in_query` values in the original parts. The distribution logic later in the code assumes contiguous indices to assign parts back to their sources. This mismatch causes parts to be assigned to wrong sources, resulting in incorrect query results.

## The Fix

The fix renumbers `part_index_in_query` to be **contiguous** starting from `added_parts`. Instead of preserving the potentially non-contiguous original indices, assign contiguous indices based on the loop counter:

1. Change the loop to use an index-based iteration with `local_idx`
2. Assign `part_index_in_query = added_parts + local_idx` (contiguous)

## What You Need To Do

1. Find the loop in `optimizeJoinByShards.cpp` that processes `analysis_result->parts_with_ranges`
2. Modify it to use index-based iteration and contiguous index assignment
3. Add an explanatory comment explaining why this is necessary (reference `filterPartsByQueryConditionCache`)
4. Ensure the fix follows ClickHouse code style

## Key Code Context

The relevant code is in the `apply()` function. Look for:
- The variable `added_parts` which tracks how many parts were already added
- The loop iterating over `analysis_result->parts_with_ranges`
- The assignment to `all_parts.back().part_index_in_query`

The fix should ensure that after filtering by query condition cache, the `part_index_in_query` values form a contiguous sequence starting from `added_parts`.

## Testing

The test file `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` demonstrates the bug scenario:
1. Creates tables with MergeTree engine
2. Populates query condition cache with a negative condition (attr != 0 matches no rows)
3. Inserts new data that should match
4. Runs JOIN query that should return results

Without the fix, the final query returns 0 rows instead of the expected 1 row.
