# Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem Description

When running JOIN queries with shard-by-primary-key optimization enabled alongside the query condition cache, the query may return **incorrect results** (specifically, 0 rows instead of the expected data).

## Bug Scenario

The issue occurs in the following sequence:

1. A JOIN query is executed with a prewhere condition that filters out all rows for a particular table part
2. The query condition cache stores this negative result (no matching rows for that part)
3. New data is inserted that would match the condition
4. A subsequent JOIN query is executed - it should return the new row, but **returns 0 rows instead**

The test file `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` demonstrates this scenario. The final SELECT statement should return 1 row with the expected output:
```
0	1	0	0
```

Without the fix, the query returns 0 rows.

## Root Cause

The shard-by-PK optimization distributes parts to different join layers. The distribution logic assumes that `part_index_in_query` values form a contiguous sequence starting from zero within each query's set of parts. However, when `filterPartsByQueryConditionCache` drops filtered parts from `selectRangesToRead()`, the original indices can become non-contiguous. This mismatch causes parts to be assigned to wrong sources, resulting in incorrect query results.

## Requirements

1. Find the code that handles JOIN shard-by-PK optimization and part index assignment in the `apply()` function
2. Ensure that `part_index_in_query` values are assigned contiguously based on the position in the loop, starting from the current value of `added_parts`
3. Add an explanatory comment explaining why contiguous indices are necessary, referencing `filterPartsByQueryConditionCache`
4. Follow ClickHouse code style (4 spaces for indentation, no trailing whitespace)

## Code Context

The relevant code is in the file `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp` in the `apply()` function that processes `JoinsAndSourcesWithCommonPrimaryKeyPrefix` structures. The fix involves the loop that iterates over `analysis_result->parts_with_ranges` and assigns `part_index_in_query` to each part.