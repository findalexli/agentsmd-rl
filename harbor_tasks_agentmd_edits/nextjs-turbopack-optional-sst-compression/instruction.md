# turbopack: Make compression in SST files optional

## Problem

The turbo-persistence crate currently always compresses SST file blocks with LZ4. However:

1. **Index blocks** contain high-entropy hash data that doesn't compress well (only a few upper bits are shared across hashes)
2. **Key blocks** also contain high-entropy hashes or small keys with similar structure, making compression ineffective
3. **Value blocks** are the only ones that achieve good compression ratios

Always compressing wastes CPU cycles for data that doesn't benefit from compression.

## Required Changes

You need to implement optional compression in the SST file format:

1. **Rename and extend ArcSlice to ArcBytes**: Replace the `ArcSlice<T>` type with `ArcBytes` that supports both `Arc<[u8]>` and memory-mapped file backing (`Arc<Mmap>`). This enables zero-copy reads for uncompressed blocks.

2. **Add compression configuration**: Create a `CompressionConfig` enum with:
   - `TryCompress { dict, long_term }` - attempt compression, only use result if it achieves at least 12.5% savings (7/8 threshold from LevelDB/RocksDB)
   - `Uncompressed` - write block as-is

3. **Update block writing logic**:
   - Write **index blocks** uncompressed (they don't benefit from compression)
   - Write **key blocks** with `TryCompress` heuristic
   - Write **value blocks** with `TryCompress` heuristic

4. **Update block format**: Use `uncompressed_size = 0` as a sentinel value to indicate uncompressed blocks:
   - Header > 0: LZ4 compressed, header value is uncompressed length
   - Header = 0: Uncompressed, actual length derived from block offsets

5. **Update documentation**: After implementing the code changes, update `turbopack/crates/turbo-persistence/README.md` to document the new Block Compression format. Add a new "Block Compression" section explaining the header format and the compressed vs uncompressed distinction.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/arc_slice.rs` — Current ArcSlice implementation (to be replaced)
- `turbopack/crates/turbo-persistence/src/lib.rs` — Module exports
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — Block writing logic
- `turbopack/crates/turbo-persistence/src/compression.rs` — Decompression logic
- `turbopack/crates/turbo-persistence/README.md` — SST file format documentation
- `turbopack/crates/turbo-persistence/src/db.rs` — Database operations using ArcSlice
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — Entry lookup using ArcSlice

## Testing

The crate should compile with `cargo check --lib`. Ensure the ArcBytes struct properly implements all traits that ArcSlice had (Deref, Borrow, Hash, PartialEq, Eq, Debug, Read) plus the new mmap support.
