# Task: Fix Wrong Results in JOIN with Shard-by-PK and Query Condition Cache

## Problem Statement

JOIN queries using shard-by-PK optimization can return **incorrect results (0 rows)** when the query condition cache is enabled and has previously cached filter results for table parts.

### Symptom

When running a JOIN query twice:
1. First run populates the query condition cache with filter results
2. A subsequent INSERT creates a new table part
3. Second run of the same JOIN query returns **0 rows instead of the expected data**

### Root Cause Analysis

The bug occurs in the shard-by-PK optimization code. The code iterates over `parts_with_ranges` and assigns `part_index_in_query` values based on the original part indices. However, `filterPartsByQueryConditionCache` may drop some parts from the results, leaving **gaps in the part_index_in_query values** (non-contiguous indices).

The downstream distribution logic assumes contiguous indices when assigning parts back to their sources. When gaps exist, parts get assigned to wrong sources, causing the JOIN to return incorrect results (0 rows).

## Requirements

The fix must satisfy ALL of the following constraints:

1. **Code correctness**: The modified code must compile without errors
2. **Style**: Follow ClickHouse Allman brace style (opening brace on its own line)
3. **Memory safety**: Do not use raw pointers or manual memory management in the fix area
4. **Behavioral correctness**: After the fix, `part_index_in_query` values must be contiguous (no gaps)

## Implementation Guidance

To fix this bug:

1. Locate the shard-by-PK optimization code that handles `parts_with_ranges` and assigns `part_index_in_query` values
2. Identify where the loop uses range-based iteration (e.g., `for (const auto & part : ...)`) which preserves the original part indices that may have gaps
3. Change the approach so that `part_index_in_query` values are assigned sequentially from a running counter, rather than preserving the original indices
4. Add comments explaining:
   - Why contiguous renumbering is necessary (the query condition cache may drop parts, causing gaps)
   - How the distribution logic depends on contiguous indices

## Code Style Requirements

- Use Allman brace style (opening brace on its own line)
- No trailing whitespace
- Use spaces, not tabs
- No raw pointers or manual memory management in the fix area

## Verification

The repository includes a test file that demonstrates the issue:
- `tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql`

The test creates tables, populates the query condition cache, inserts new data, and verifies the JOIN returns correct results (expecting `0 1 0 0` output).
