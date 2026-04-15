# Task: Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem Statement

JOIN queries using shard-by-PK optimization can return **incorrect results (0 rows)** when the query condition cache is enabled and has previously cached filter results for table parts.

### Symptom

When running a JOIN query twice:
1. First run populates the query condition cache with filter results
2. A subsequent INSERT creates a new table part
3. Second run of the same JOIN query returns **0 rows instead of the expected data**

### Affected Component

The bug is in `apply()` function in `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp`.

### Requirements

The fix must satisfy ALL of the following constraints:

1. **Code correctness**: The modified code must compile without errors
2. **Style**: Follow ClickHouse Allman brace style (opening brace on its own line)
3. **Memory safety**: Do not use raw pointers or manual memory management in the fix area
4. **Output requirements**: The final source file must contain:
   - A `for` loop using `size_t local_idx` as the loop variable
   - Index access pattern: `analysis_result->parts_with_ranges[local_idx]`
   - Index assignment using: `part_index_in_query = added_parts + local_idx`
   - A comment containing the exact text: `Renumber part_index_in_query to be contiguous`
   - A comment containing the exact text: `filterPartsByQueryConditionCache may drop parts`

### Verification

The repository includes a test file that demonstrates the issue:
- `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql`

The test creates tables, populates the query condition cache, inserts new data, and verifies the JOIN returns correct results (expecting `0 1 0 0` output).