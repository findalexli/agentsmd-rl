# Make compression in SST files optional

## Problem

The `turbo-persistence` crate currently compresses every block (index, key, and value) in SST files unconditionally. However, index blocks and many key blocks consist of high-entropy hash data that compresses poorly — the compressed output is often the same size or larger than the input, wasting CPU time on both read and write paths.

Additionally, the `ArcSlice<T>` type used throughout the crate is generic but only ever instantiated as `ArcSlice<u8>`. It doesn't support memory-mapped file backing, which means even blocks that were stored uncompressed must still be copied into heap-allocated buffers on read.

## Expected Behavior

1. **Compression should be optional per block type.** Index blocks should always be stored uncompressed. Key and value blocks should attempt compression but fall back to uncompressed storage when compression doesn't achieve meaningful savings (following the LevelDB/RocksDB 7/8 threshold heuristic).

2. **The on-disk format needs a sentinel value** to distinguish compressed from uncompressed blocks. A header value of 0 should indicate an uncompressed block (actual length derived from offsets), while a positive header value indicates the uncompressed length of an LZ4-compressed block.

3. **Replace `ArcSlice<T>` with a specialized `ArcBytes` type** that supports both `Arc<[u8]>` and `Arc<Mmap>` backing. This enables zero-copy reads for uncompressed blocks directly from the memory-mapped file.

4. **Update the crate's README** to document the new block compression format, including the header semantics and how compressed vs uncompressed blocks are distinguished.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/arc_slice.rs` — current generic `ArcSlice<T>`, needs replacement
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — block writing logic, needs compression config
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — block reading logic, needs uncompressed handling
- `turbopack/crates/turbo-persistence/src/lib.rs` — module declarations and public exports
- `turbopack/crates/turbo-persistence/src/db.rs` — uses `ArcSlice` type
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — value lookup types
- `turbopack/crates/turbo-persistence/README.md` — on-disk format documentation
