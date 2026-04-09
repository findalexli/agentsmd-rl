# Fix JOIN with shard-by-PK and query condition cache producing wrong results

## Problem

The `optimizeJoinByShards` optimization in ClickHouse produces **wrong results** (returns 0 rows instead of actual data) when used together with the query condition cache.

## Location

The bug is in `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp` in the `apply()` function.

## Root Cause

The optimization assumes that `part_index_in_query` values are **contiguous** when distributing parts back to their sources. However, `filterPartsByQueryConditionCache` can drop some parts from `selectRangesToRead()`, leaving **gaps** in the indices. The distribution logic then assigns parts to the wrong source.

## What Needs to Change

The code needs to **renumber** `part_index_in_query` to be contiguous starting from `added_parts`. Instead of:

```cpp
for (const auto & part : analysis_result->parts_with_ranges)
{
    all_parts.push_back(part);
    all_parts.back().part_index_in_query += added_parts;
}
```

It should use an explicit index counter:

```cpp
for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
{
    all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);
    all_parts.back().part_index_in_query = added_parts + local_idx;
}
```

This ensures that even when parts are dropped by the query condition cache, the remaining parts have contiguous indices for correct distribution.

## Hints

- Look for the loop that populates `all_parts` from `analysis_result->parts_with_ranges`
- The key is assigning `part_index_in_query` based on the position in the loop, not the original value
- Add a comment explaining why the renumbering is necessary

## Reference

- Original PR: #100926
- Backport PR: #101962
- The test case in `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` demonstrates the bug scenario
