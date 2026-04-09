# Fix materialize_skip_indexes_on_merge not suppressing text indexes

## Problem

When `materialize_skip_indexes_on_merge` is set to `false`, text (full-text) indexes are still being built during merge operations. Other skip index types (minmax, set, bloom_filter) are correctly suppressed when this setting is disabled, but text indexes continue to be built, wasting CPU and I/O resources.

## Context

Text indexes in ClickHouse use a separate container for handling during vertical merges (introduced in PR #74401). This separate container is not being cleared when `materialize_skip_indexes_on_merge=false`, unlike the containers used for other skip index types.

## Files to Modify

- `src/Storages/MergeTree/MergeTask.cpp` - Look around line 881-886 where skip indexes are handled during merge preparation

## Expected Behavior

When `materialize_skip_indexes_on_merge` is `false`:
1. All skip index types should be suppressed during merge, including text indexes
2. The existing suppression logic clears `merging_skip_indexes` and `skip_indexes_by_column`
3. Text indexes should be similarly suppressed

## Testing

The fix should be verified by:
1. Code compilation succeeds
2. The fix properly handles the text index container in the same code path as other skip indexes
3. Code style follows the project's Allman brace convention (opening brace on new line)

## References

- Related issue: #101666
- Target file: `src/Storages/MergeTree/MergeTask.cpp`
- Look for the `ExecuteAndFinalizeHorizontalPart::prepare()` function
