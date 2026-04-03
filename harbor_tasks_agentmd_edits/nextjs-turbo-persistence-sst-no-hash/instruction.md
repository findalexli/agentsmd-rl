# Allow key blocks without hash in SST files

## Problem

The turbo-persistence crate's SST (Static Sorted Table) file format wastes storage by always storing an 8-byte hash for every key entry, even when keys are short enough that the hash can be cheaply recomputed. This is noted as a TODO in the format documentation:

> TODO: 8 bytes key hash is a bit inefficient for small keys.

For keys of 32 bytes or less, storing the full hash doubles the overhead unnecessarily — the hash could be recomputed on demand with minimal CPU cost.

## Expected Behavior

The SST format should support a new key block variant that omits per-entry hashes. Specifically:

- Introduce a second key block type (alongside the existing one) that stores keys without per-entry hashes
- The builder should decide which block type to use based on the maximum key length in the block — short keys (≤ 32 bytes) don't need stored hashes
- The reader/lookup code must handle both block types: reading stored hashes when present, or recomputing them from the key data when absent
- The iterator must also handle both block types correctly

After making the code changes, update the crate's README.md to document the new format variant. The on-disk format specification should reflect the two block types and their differences.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST reader, lookup, and iterator logic; defines block type constants
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST writer; `KeyBlockBuilder` writes key blocks
- `turbopack/crates/turbo-persistence/README.md` — On-disk format specification documenting the SST layout
