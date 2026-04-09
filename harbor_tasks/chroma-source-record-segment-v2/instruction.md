# Create SourceRecordSegmentV2Operator for Segment Rebuild

## Problem

The segment rebuild path needs a new operator that combines the functionality of `SourceRecordSegment`, `Partition`, and `MaterializeLog` operators into a single streaming operator. The current approach requires multiple discrete steps and doesn't efficiently handle the specific requirements of the rebuild path.

## What You Need to Do

Create a new `SourceRecordSegmentV2Operator` in `rust/worker/src/execution/operators/source_record_segment_v2.rs` that:

1. **Streams through the record segment** and produces partitioned materialized log records
2. **Uses `max_partition_size`** to split records into partitions
3. **Preserves offset IDs** from the existing record segment
4. **Only allows `Add` operations** - returns an error for any other operation type (Upsert, Delete, Update)
5. **Returns empty partitions** when the record segment reader is `None`

You also need to:

6. **Add a `materialize_logs_for_rebuild` function** in `rust/segment/src/types.rs` that:
   - Takes logs and offset_ids as parameters
   - Validates all operations are `Add`
   - Returns `UnsupportedOperationForRebuild` error for non-Add operations
   - Sets `offset_id_exists_in_segment = true` and `final_operation = MaterializedLogOperation::AddNew`

7. **Update `SourceRecordSegmentOperator`** in `rust/worker/src/execution/operators/source_record_segment.rs`:
   - Add a `new()` constructor
   - Add a `Default` implementation
   - Change the operation from `Upsert` to `Add`
   - Update tests to expect `Operation::Add`

8. **Integrate in `LogFetchOrchestrator`**:
   - Add imports for the new V2 types
   - Use `SourceRecordSegmentV2Operator` for partial rebuilds (non-full rebuilds)
   - Keep using `SourceRecordSegmentOperator` for full rebuilds
   - Implement a handler for `SourceRecordSegmentV2Output`
   - Update the `record_reader` logic to filter when rebuilding

9. **Add error variant** in `LogFetchOrchestratorError` for `SourceRecordSegmentV2`

10. **Add unit tests** for the V2 operator covering:
    - Basic functionality with 100 records partitioned correctly
    - Empty reader handling
    - Offset ID preservation

## Files to Modify

- `rust/worker/src/execution/operators/source_record_segment_v2.rs` (new file)
- `rust/worker/src/execution/operators/mod.rs`
- `rust/worker/src/execution/operators/source_record_segment.rs`
- `rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs`
- `rust/segment/src/types.rs`

## Key Behaviors

- The V2 operator should use `materialize_logs_for_rebuild` to materialize each partition
- For rebuild operations, only `Add` operations are valid - any other operation type should fail
- Partitions are created when `current_partition_logs.len() >= max_partition_size`
- The operator produces `MaterializeLogOutput` for each partition
- When reader is `None`, return empty partitions and `total_records = 0`

## Testing

After implementing, verify:
1. `cargo check --package chroma-worker` compiles successfully
2. `cargo test --package chroma-worker source_record_segment` passes all tests

The V2 operator tests should verify partitioning logic, operation types, and offset ID preservation.
