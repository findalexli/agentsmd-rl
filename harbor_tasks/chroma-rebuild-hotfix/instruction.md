# Fix Rebuild Operation Handling in Chroma's Compaction Pipeline

## Problem

The Chroma vector database's compaction pipeline has an issue with rebuild operations. When performing a metadata-only rebuild of a collection, the system needs to:

1. **Stream and partition records**: Large record segments need to be processed in manageable partitions during rebuild operations, but the current implementation doesn't handle this efficiently.

2. **Use correct operation type**: The `SourceRecordSegmentOperator` currently produces records with `Operation::Upsert`, but rebuild operations should use `Operation::Add` since they're reconstructing the segment from scratch.

3. **Validate operations for rebuild**: During a rebuild, only "Add" operations are valid. The system needs a specialized materialization function that enforces this constraint.

## Files to Modify

The relevant code is in the `rust/` directory:

- `rust/segment/src/types.rs` - Contains materialization logic for log records
- `rust/worker/src/execution/operators/source_record_segment.rs` - Original record sourcing operator
- `rust/worker/src/execution/operators/mod.rs` - Module exports
- `rust/worker/src/execution/operators/source_record_segment_v2.rs` - **Create this new file** for the V2 operator
- `rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs` - Orchestrator that coordinates the rebuild flow
- `rust/worker/src/execution/orchestration/compact.rs` - Contains compaction/rebuild tests

## Requirements

You need to implement:

1. A new `materialize_logs_for_rebuild()` function in `rust/segment/src/types.rs` that:
   - Accepts a chunk of log records and their offset IDs
   - Validates that all operations are "Add" (rejects Upsert/Delete/Update with an error)
   - Sets appropriate flags for rebuild scenarios (`offset_id_exists_in_segment = true`, `final_operation = AddNew`)
   - Returns `has_backfill: false` since rebuilds never have backfill

2. A new `SourceRecordSegmentV2Operator` in a new file `source_record_segment_v2.rs` that:
   - Streams through the record segment using the record segment reader
   - Creates log records with `Operation::Add` (not Upsert)
   - Partitions the output into chunks based on `max_partition_size`
   - Calls `materialize_logs_for_rebuild()` for each partition
   - Returns the materialized partitions and total record count
   - Has unit tests for basic operation, empty input, and offset ID preservation

3. Updates to `SourceRecordSegmentOperator`:
   - Add a `new()` constructor and `Default` implementation
   - Change the operation type from `Upsert` to `Add` in the output records
   - Update the corresponding unit test expectations

4. Integration in `log_fetch_orchestrator.rs`:
   - Import the V2 operator types and add the corresponding error variant
   - In the rebuild flow, conditionally use `SourceRecordSegmentV2Operator` (for partial rebuilds) vs the original operator
   - Add a handler for the V2 operator output that processes the partitioned results

5. Module export:
   - Add `pub mod source_record_segment_v2` to `rust/worker/src/execution/operators/mod.rs`

## Testing

The solution should pass these verifications:

- Rust code compiles without errors
- `SourceRecordSegmentV2Operator` correctly partitions 100 records into chunks of 30
- The operator handles empty input gracefully (returns empty partitions)
- Offset IDs are preserved correctly through the materialization process
- `SourceRecordSegmentOperator` uses `Operation::Add` (not `Operation::Upsert`)
- The new `materialize_logs_for_rebuild` function exists with proper error handling
- The orchestrator properly integrates the V2 operator for rebuild flows

## Notes

- The V2 operator is designed for partial rebuilds (metadata-only), while full rebuilds continue using the original operator
- The error variant `UnsupportedOperationForRebuild` should be added to `LogMaterializerError` for when non-Add operations are encountered
- The partition size is configurable via `max_partition_size` parameter
- Look at existing operator patterns in the codebase for implementation guidance
