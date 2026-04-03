# Make compression in SST files optional for turbo-persistence

## Problem

The `turbo-persistence` crate in Turbopack compresses all blocks in SST files using LZ4, but not all block types benefit from compression. Index blocks contain high-entropy hash-to-block-index pairs where the hashes have very little redundancy. Key blocks similarly store high-entropy hashes or small keys. Compressing these blocks wastes CPU time on both the write and read paths for negligible (or zero) space savings.

Additionally, the current `ArcSlice<T>` type used for byte slice management is generic over `T` but only ever instantiated with `u8`. It also lacks support for memory-mapped file backing, forcing unnecessary copies when reading uncompressed data from mmap'd SST files.

## Expected Behavior

1. **Optional block compression**: The SST file writer should skip compression for blocks where it doesn't help. Use industry-standard heuristics (e.g., the LevelDB/RocksDB approach: only store compressed if the result is smaller than 7/8 of the original). Index blocks should never be compressed. The 4-byte block header should use `0` as a sentinel to indicate uncompressed blocks, with the actual length derived from block offsets.

2. **Zero-copy reads for uncompressed blocks**: On the read side, when a block header indicates `0` (uncompressed), return a slice directly into the memory-mapped file instead of copying/decompressing. This requires the byte slice type to support mmap backing.

3. **Replace `ArcSlice` with `ArcBytes`**: Since the type is only used for `[u8]`, replace the generic `ArcSlice<T>` with a specialized `ArcBytes` that can be backed by either an `Arc<[u8]>` or an `Arc<Mmap>`. Update all references throughout the crate and its consumers.

4. **Rename `MediumCompressed` to `MediumRaw`**: The `EntryValue::MediumCompressed` variant should be renamed since blocks may now be stored uncompressed. The `uncompressed_size` field uses `0` to indicate the block is stored raw.

After making the code changes, update the crate's README to document the new block compression format so future developers understand when blocks are compressed vs. uncompressed.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/arc_slice.rs` — current byte slice type (to be replaced)
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST file writer
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST file reader
- `turbopack/crates/turbo-persistence/src/lib.rs` — crate root, module declarations and public exports
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — lookup value types
- `turbopack/crates/turbo-persistence/src/db.rs` — database layer using the byte slice type
- `turbopack/crates/turbo-persistence/README.md` — crate documentation (needs update)
- `turbopack/crates/turbo-tasks-backend/src/database/turbo/mod.rs` — consumer of the public API
