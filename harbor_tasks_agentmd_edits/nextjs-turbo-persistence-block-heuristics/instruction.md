# Turbo-persistence: Improve block sizing heuristics and prevent block index overflow

## Problem

The `turbo-persistence` crate in Turbopack has several issues with its block sizing constants and heuristics:

1. **Small value threshold too large**: `MAX_SMALL_VALUE_SIZE` is set to 64 KiB, which means values up to 64 KiB are packed into shared blocks. This is too aggressive — values in the 4–64 KiB range would benefit from being stored in dedicated blocks where they can be copied without decompression during compaction.

2. **Block emission uses maximum instead of minimum**: Small value blocks are capped at a maximum size rather than emitted once they reach a minimum size. This leads to suboptimal block sizes.

3. **No block count overflow protection**: There is no mechanism to prevent exceeding the u16 block index limit in SST files. With many small values, the block count can overflow during compaction (specifically during the 50/50 merge-and-split), causing panics in CI benchmarks.

4. **Inaccurate overhead constant**: `KEY_BLOCK_ENTRY_META_OVERHEAD` is 8, but the actual worst-case overhead per entry in a key block is larger when accounting for type, position, hash, block index, size, and position-in-block fields.

## Expected Behavior

- Values up to 4 KiB should be "small" (packed into shared value blocks). Values 4 KiB to 64 MB should be "medium" (dedicated blocks, copyable during compaction without decompression). This gives a better balance between compression efficiency and access cost.
- Small value blocks should be emitted once they accumulate a minimum amount of data (e.g., 8 KiB), producing blocks in the 8–12 KiB range.
- A tracker should prevent the value block count from exceeding the u16 index limit, splitting into a new SST file when the limit is approached.
- The key block entry overhead constant should reflect the actual worst-case byte count.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/constants.rs` — block sizing constants
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — block emission logic and entry overhead constant
- `turbopack/crates/turbo-persistence/src/collector.rs` — collector that decides when to flush to a new file
- `turbopack/crates/turbo-persistence/src/collector_entry.rs` — entry value classification methods
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — lookup value classification methods
- `turbopack/crates/turbo-persistence/src/db.rs` — compaction logic that needs overflow protection
- `turbopack/crates/turbo-persistence/README.md` — value type documentation (update to reflect the new type hierarchy and size boundaries)

After making the code changes, update the crate's README to accurately document the value types, their size ranges, and the trade-offs between them (compression, compaction cost, access cost, storage overhead).
