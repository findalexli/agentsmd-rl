# Fix wrong results in JOIN with shard-by-PK and query condition cache

## Problem Description

The `optimizeJoinByShards` optimization in ClickHouse is producing wrong (empty) results when used together with the query condition cache.

### The Bug

In `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp`, the `apply()` function distributes parts across sources based on their `part_index_in_query` values. However, when `filterPartsByQueryConditionCache` drops parts during `selectRangesToRead()`, the remaining parts have **non-contiguous** `part_index_in_query` values.

The distribution logic assumes contiguous indices to assign parts back to their sources. When parts are dropped by the cache (leaving gaps in the indices), the remaining parts get adjusted indices that fall outside the expected range for their source. This causes them to be assigned to no source, resulting in t1 reading 0 rows and producing incorrect empty JOIN results.

### Example Scenario

1. Source t1 has parts at indices [0, 1]
2. Index 0 is dropped by the cache (it cached that the condition evaluates to false for that part)
3. The remaining part at index 1 gets an adjusted global index that falls outside the expected range for source t1
4. Result: t1 reads 0 rows, JOIN produces wrong empty result

### Required Fix

The fix must renumber `part_index_in_query` to be contiguous when collecting parts from each source. Instead of:

```cpp
for (const auto & part : analysis_result->parts_with_ranges)
{
    all_parts.push_back(part);
    all_parts.back().part_index_in_query += added_parts;
}
```

The code should use a local index variable:

```cpp
for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
{
    all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);
    all_parts.back().part_index_in_query = added_parts + local_idx;
}
```

### Style Requirements

This codebase follows ClickHouse style conventions:
- Use **Allman-style braces** (opening brace on new line) - this is enforced by CI
- Use **lowercase_with_underscores** for variable names
- **Never use sleep** in C++ code to fix race conditions
- When referring to functions in comments, write `function_name` not `function_name()`
- Complex logic should have explanatory comments

### Files to Modify

- `src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp` - The apply() function around line 238

### Verification

The fix should:
1. Use a local index loop variable (`local_idx`)
2. Assign `part_index_in_query = added_parts + local_idx`
3. Include an explanatory comment about why this is needed (filterPartsByQueryConditionCache dropping parts)
4. Follow Allman brace style
