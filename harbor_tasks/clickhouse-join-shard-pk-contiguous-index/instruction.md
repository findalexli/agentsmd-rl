# Task: Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem

JOIN queries with shard-by-PK optimization can return **wrong results (0 rows)** when the query condition cache is enabled and has previously cached filter results for table parts.

### Symptom

When running a JOIN query twice:
1. First run populates the query condition cache with filter results
2. A subsequent INSERT creates a new table part
3. Second run of the same JOIN query returns **0 rows instead of the expected data**

### Affected File

`src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp`

The bug is in the `apply()` function which processes parts for distributed JOIN optimization. The code incorrectly assumes that `part_index_in_query` values are contiguous, but `filterPartsByQueryConditionCache()` can drop parts, leaving gaps in the indices. This causes the layer distribution logic to assign parts to the wrong sources.

### What You Need to Do

1. Locate the section in `apply()` that processes `analysis_result->parts_with_ranges`
2. Identify where `part_index_in_query` is being set
3. Fix the index assignment to ensure contiguous indices (starting from `added_parts`) regardless of which parts were dropped by the query condition cache
4. Add a comment explaining why contiguous renumbering is necessary

### Code Context

Look for the loop that iterates over `analysis_result->parts_with_ranges` and pushes parts to `all_parts`. The current code preserves the original `part_index_in_query` values with an offset, but this breaks when parts are filtered out by the cache.

### Constraints

- Follow the existing code style (Allman braces - opening brace on new line)
- Do not use raw pointers or manual memory management
- Keep changes minimal and focused on the bug
- Add an explanatory comment about the fix

### Testing

The repository includes a test file that demonstrates the issue:
- `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql`

The test creates tables, populates the query condition cache, inserts new data, and verifies the JOIN returns correct results (expecting `0 1 0 0` output).
