# Task: Add Sharding Fields to Scan Types

## Problem Description

The query execution system needs to support sharded query execution in the future. To enable this, the `Scan` data structure needs to carry three new fields that indicate which shard a worker should process:

1. `shard_index` - Which shard this worker is responsible for querying
2. `num_shards` - Total number of shards for the collection (0 means unsharded, should default to 1)
3. `log_upper_bound_offset` - Upper bound log offset scouted by the frontend (0 means worker scouts independently)

## What You Need to Do

1. **Add fields to protobuf message** (`idl/chromadb/proto/query_executor.proto`):
   - Add `shard_index` (uint32, field 8) to `ScanOperator` message
   - Add `num_shards` (uint32, field 9) to `ScanOperator` message
   - Add `log_upper_bound_offset` (int64, field 10) to `ScanOperator` message

2. **Add fields to Rust struct** (`rust/types/src/execution/operator.rs`):
   - Add the three fields to the `Scan` struct with appropriate types
   - Update `TryFrom<ScanOperator>` to extract these fields from protobuf, with backward compatibility: if `num_shards` is 0, default it to 1
   - Update `TryFrom<Scan>` for `chroma_proto::ScanOperator` to include these fields in the proto output

3. **Update all places that construct `Scan`** - Search for all places in the codebase that instantiate `Scan` structs and add the three new fields with default values (shard_index=0, num_shards=1, log_upper_bound_offset=0). These will primarily be in:
   - Frontend implementations
   - Test code

## Requirements

- The changes must maintain backward compatibility: if `num_shards` is 0 (absent in proto), treat it as 1 (unsharded)
- All existing tests should continue to compile and pass
- The code must compile without errors

## Hints

- The protobuf file uses field numbers 1-7 already, continue with 8, 9, 10
- For the Rust struct, the types should match the protobuf: `u32` for shard_index/num_shards, `i64` for log_upper_bound_offset
- Look for `Scan { collection_and_segments: ... }` patterns in the codebase
- The test files will need the new fields added to their Scan construction
