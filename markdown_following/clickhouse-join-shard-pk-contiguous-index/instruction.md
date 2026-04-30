# Task: Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem Statement

JOIN queries using shard-by-PK optimization can return **incorrect results (0 rows)** when the query condition cache is enabled and has previously cached filter results for table parts.

## Symptom

When running a JOIN query twice:
1. First run populates the query condition cache with filter results
2. A subsequent INSERT creates a new table part
3. Second run of the same JOIN query returns **0 rows instead of the expected data**

The SQL test file `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` demonstrates this issue and the reference file `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.reference` expects output: `0 1 0 0`.

## Code Location

The bug is in the shard-by-PK optimization code in `optimizeJoinByShards::apply()`, located in:

```
src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp
```

The function iterates over `analysis_result->parts_with_ranges` and assigns `part_index_in_query` values to parts collected into `all_parts`. The variable `added_parts` tracks how many parts were already in `all_parts` before the current source.

The `selectRangesToRead()` call populates `parts_with_ranges`. Internally, `selectRangesToRead()` calls `filterPartsByQueryConditionCache`, which may drop some parts from the results when the query condition cache has previously cached filter results.

The downstream distribution logic assigns parts back to their original sources based on `part_index_in_query` values. This logic expects the values to be **contiguous** (no gaps). When `filterPartsByQueryConditionCache` drops parts, the original `part_index_in_query` values from `parts_with_ranges` can be non-contiguous, causing parts to be assigned to the wrong sources and producing incorrect JOIN results.

## Requirements

The fix must satisfy ALL of the following constraints:

1. **Behavioral correctness**: After the fix, the JOIN must return the correct results (matching reference output `0 1 0 0`) even when the query condition cache has previously cached filter results that cause `selectRangesToRead()` to return fewer parts than originally present
2. **Contiguous part_index_in_query**: The `part_index_in_query` values assigned to parts must be contiguous (no gaps), so the downstream distribution logic correctly maps parts back to their sources
3. **Code correctness**: The modified code must compile without errors

## Code Style Requirements

- Use **Allman brace style** (opening brace on its own line, per ClickHouse C++ style guide)
- No trailing whitespace
- Use spaces, not tabs
- No raw pointers or manual `new`/`delete` memory management in the fix area
- Source files must not be executable, must have no BOM, must be tracked by git with mode 100644

## Explanation

The fix should include a clear explanation (as a code comment) of why the change is needed. The comment should describe the interaction with `filterPartsByQueryConditionCache` and why contiguous renumbering of `part_index_in_query` is necessary.

## Verification

The repository includes test files that demonstrate the issue:
- `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql` — SQL test that creates tables, populates the query condition cache, inserts new data, and verifies the JOIN returns correct results
- `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.reference` — expected output `0 1 0 0`
