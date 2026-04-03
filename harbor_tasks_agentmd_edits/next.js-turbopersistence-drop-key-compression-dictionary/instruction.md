# Drop key compression dictionary from turbo-persistence SST files

## Problem

The `turbo-persistence` crate (`turbopack/crates/turbo-persistence/`) currently uses a zstd compression dictionary for key blocks in SST files, while value blocks already use plain LZ4. This dual compression scheme adds unnecessary complexity: the zstd dependency, dictionary computation during SST file building, dictionary-aware decompression paths, and extra metadata fields to track dictionary size.

The key compression dictionary needs to be removed to simplify the on-disk format and unblock streaming SST writes.

## Expected Behavior

After the refactor:

1. **All blocks** (key, index, and value) should use plain LZ4 compression — no more zstd dictionary.
2. The `zstd` dependency should be removed from the crate's `Cargo.toml`.
3. Compression and decompression functions in `src/compression.rs` should be simplified to remove dictionary and `long_term` parameters.
4. The `StaticSortedFileMetaData` struct should no longer carry a `key_compression_dictionary_length` field.
5. The meta file reader/writer should no longer read/write the dictionary length field.
6. The SST file builder should no longer compute or write a key compression dictionary.
7. The `sst_inspect` tool should be updated to work without dictionary logic.
8. **The crate's README.md documentation should be updated** to reflect the new on-disk format — the meta file format no longer includes a dictionary length field, SST files no longer start with a serialized dictionary, and the compression description should reference LZ4 directly.

## Files to Look At

- `turbopack/crates/turbo-persistence/Cargo.toml` — crate dependencies (remove zstd)
- `turbopack/crates/turbo-persistence/src/compression.rs` — compression/decompression functions
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST file reader and metadata
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST file writer and dictionary computation
- `turbopack/crates/turbo-persistence/src/meta_file.rs` — meta file reader
- `turbopack/crates/turbo-persistence/src/meta_file_builder.rs` — meta file writer
- `turbopack/crates/turbo-persistence/src/db.rs` — database layer using SST files
- `turbopack/crates/turbo-persistence/src/write_batch.rs` — write batch operations
- `turbopack/crates/turbo-persistence/src/bin/sst_inspect.rs` — inspection tool
- `turbopack/crates/turbo-persistence/benches/mod.rs` — benchmarks
- `turbopack/crates/turbo-persistence/README.md` — on-disk format documentation
- `Cargo.lock` — lock file (will update when zstd is removed)
