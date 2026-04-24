# Task: Fix delete_metrics_splits Error Handling in PostgreSQL Metastore

## Problem Description

The `delete_metrics_splits` function in the PostgreSQL metastore has incorrect error handling behavior. When asked to delete splits that are **not marked for deletion** (i.e., splits in `Staged` or `Published` state), the function silently succeeds without actually deleting them. The caller receives success but the splits remain untouched.

**Expected behavior** (matching the pattern used by the non-metrics `delete_splits` function):
- When any split is in `Staged` or `Published` state, the function should return a `FailedPrecondition` error listing the split IDs
- When splits genuinely don't exist, the function should log a warning and return success (idempotent behavior — this already works correctly)

## Files to Modify

1. **`quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs`** — the `delete_metrics_splits` async function
2. **`quickwit/quickwit-parquet-engine/src/split/metadata.rs`** — the `row_keys_proto` field's doc comment in `MetricsSplitMetadata`

## What to Do

### For the metastore fix:

The current implementation silently succeeds when splits can't be deleted. You need to distinguish between three cases:

1. Splits that exist and are `MarkedForDeletion` → delete them
2. Splits that exist but are in `Staged` or `Published` state → return `FailedPrecondition` with the split IDs
3. Splits that don't exist → log a warning but return success (idempotent)

The function should use a single query that can distinguish all three cases and return information sufficient to determine which case applies.

### For the doc comment fix:

Update the doc comment for `row_keys_proto` to reference the actual proto type used for serialization.

## Verification

After your fix, these patterns should be present in the code:

1. The `DELETE_SPLITS_QUERY` uses a CTE pattern (not a simple DELETE)
2. The query returns counts and arrays that distinguish deletable vs. non-deletable splits
3. There's a check that returns `FailedPrecondition` when splits are in `Staged` or `Published` state
4. There's a warning for splits that weren't found (idempotent behavior)
5. The `row_keys_proto` doc comment references `sortschema::RowKeys` and `event_store_sortschema.proto`

## Reference

The working `delete_splits` function (non-metrics version) in the same file already implements this pattern correctly and can be used as a reference for the expected error handling behavior.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
