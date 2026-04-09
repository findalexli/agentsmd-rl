# Bug: Vector Segment Rebuilds Lose Record Offset ID References

## Problem Description

When Chroma performs a **vector-only segment rebuild** (rebuilding only the vector/HNSW index without rebuilding the record segment), the rebuilt vector segment loses synchronization with the existing record segment's offset IDs. This causes data inconsistency where the vector index refers to incorrect or non-existent record offsets.

## Symptoms

- After a vector-only rebuild, vector segment offset IDs don't match record segment offset IDs
- Records that exist in the record segment may not be findable through the vector index
- The issue manifests when records have been deleted and then a vector-only rebuild is triggered

## Affected Components

The bug is in the compaction orchestration logic:

1. **`rust/worker/src/execution/orchestration/compact.rs`** - The `CompactionContext` needs to properly distinguish between full rebuilds (RECORD scope) and partial rebuilds (VECTOR scope only)

2. **`rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs`** - The `LogFetchOrchestrator` incorrectly filters out the record reader during all rebuilds, when it should only filter it out during full (RECORD scope) rebuilds

3. **`rust/worker/src/execution/operators/source_record_segment.rs`** - Records sourced from the existing record segment during rebuild should be treated as `Upsert` operations, not `Add` operations

4. **`rust/worker/src/execution/orchestration/apply_logs_orchestrator.rs`** - Size calculations need to account for the type of rebuild being performed

5. **`rust/segment/src/distributed_hnsw.rs`** - May need a method to query all offset IDs for verification

## Root Cause

When `scope_is_active(VECTOR)` is set but `scope_is_active(RECORD)` is not set (vector-only rebuild), the system currently:
1. Still filters out the record reader because `is_rebuild` is true
2. Cannot access pre-existing offset IDs from the record segment
3. Creates a vector index with incorrect offset mappings

## What Needs to Happen

The system should:
1. Distinguish between a "full rebuild" (RECORD scope is active) and a "partial rebuild" (VECTOR only)
2. Keep the record reader available during partial rebuilds so offset IDs can be referenced
3. Continue to yield `Upsert` operations (not `Add`) when sourcing from existing records
4. Pass the `apply_segment_scopes` through the orchestrator chain so downstream components can make scope-aware decisions

## Testing Approach

The fix includes a test (`test_rebuild_vector_only`) that:
1. Creates segments with some records
2. Deletes specific records
3. Performs a vector-only rebuild (VECTOR scope only)
4. Verifies that offset IDs in the vector segment still match those in the record segment

Your task is to implement the fix so that vector-only rebuilds correctly retain and reference the record segment's offset IDs.
