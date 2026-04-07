# Improve turbo-persistence block sizing heuristics

## Problem

The turbo-persistence crate in Turbopack has suboptimal block sizing constants that lead to poor compaction behavior. Specifically:

1. **`MAX_SMALL_VALUE_SIZE` is too large at 64KB.** Values up to 64KB are packed into shared small value blocks, but this means huge blocks that are expensive to decompress on every lookup. Values above ~4KB should be stored in dedicated medium value blocks that can be copied without decompression during compaction.

2. **Small value block emission uses a maximum size instead of a minimum.** The current `MAX_SMALL_VALUE_BLOCK_SIZE` (64KB) logic emits blocks only when they hit a ceiling. This should be inverted: blocks should be emitted once they accumulate a minimum amount of data (e.g., 8KB), so actual block sizes stay in the 8-12KB range for good compression without needing a dictionary.

3. **`KEY_BLOCK_ENTRY_META_OVERHEAD` is 8, but the actual worst-case overhead per entry is 20 bytes** (1 type + 3 position + 8 hash + 2 block index + 2 size + 4 position in block). This causes key blocks to be overfilled.

4. **No protection against u16 block index overflow.** When an SST file accumulates too many value blocks (especially with many small or medium values), the block count can exceed `u16::MAX`, causing a panic in CI benchmarks. A tracker is needed to split SST files before they overflow.

## Expected Behavior

- `MAX_SMALL_VALUE_SIZE` should be reduced to 4096 bytes, so values above 4KB become medium values with dedicated blocks.
- A new `MIN_SMALL_VALUE_BLOCK_SIZE` constant (8KB) should control when small value blocks are emitted.
- `KEY_BLOCK_ENTRY_META_OVERHEAD` should be updated to 20.
- A new `ValueBlockCountTracker` should be added to prevent exceeding the u16 block index limit, integrated into both the `Collector` and the compaction path in `db.rs`.
- The `write_value_blocks` function in `static_sorted_file_builder.rs` must use the new minimum-based emission logic.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/constants.rs` — sizing constants
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — value block writing logic and meta overhead
- `turbopack/crates/turbo-persistence/src/collector.rs` — entry collection with overflow tracking
- `turbopack/crates/turbo-persistence/src/collector_entry.rs` — entry value classification helpers
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — lookup value classification for compaction
- `turbopack/crates/turbo-persistence/src/db.rs` — compaction path overflow integration
- `turbopack/crates/turbo-persistence/src/lib.rs` — module registration

After making the code changes, update the crate's README to reflect the new value type boundaries and sizing behavior. The project's CLAUDE.md emphasizes keeping README documentation in sync with code changes.
