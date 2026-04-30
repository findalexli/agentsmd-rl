# Allow key blocks without hash in SST files

## Problem

The turbo-persistence crate's SST (Static Sorted Table) file format currently stores an 8-byte hash for every key entry in key blocks. This is wasteful for short keys where the hash can be cheaply recomputed from the key data itself. The existing README even has a TODO noting this: "8 bytes key hash is a bit inefficient for small keys."

## Expected Behavior

The SST format should support a new key block variant that omits the per-entry hash. For keys that are short enough (32 bytes or fewer), the block builder should produce blocks without stored hashes, and the reader should recompute hashes on demand during lookups. This requires:

1. A new block type constant for "key block without hash"
2. Logic to decide when to omit hashes based on maximum key length in the block
3. Updated read/lookup paths that handle both block variants (with and without stored hashes)
4. Updated key comparison that can recompute hashes when they are not stored
5. Updated iterator to handle variable-length hash entries

After making the code changes, update the crate's README.md to reflect the new block format — it serves as the on-disk format specification and must accurately describe both block type variants, the conditional hash storage, and the key length threshold.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST reader, lookup, and iterator logic
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST writer and key block builder
- `turbopack/crates/turbo-persistence/README.md` — on-disk format specification
