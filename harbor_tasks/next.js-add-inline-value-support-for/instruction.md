# Implement Inline Value Storage in SST Key Blocks

## Problem

The turbo-persistence crate's Static Sorted Table (SST) file format currently stores all values in separate value blocks, even when the value is very small (e.g., 1-8 bytes). For these tiny values, the 8 bytes of indirection metadata (block index, size, position) used to reference the value block is as large as or larger than the value itself. This wastes space and adds an unnecessary extra lookup on reads.

The key block entry type encoding already reserves types 8-255 for inline values (documented as "future" in the README), but the feature was never implemented — the code currently bails with an error for any entry type >= 8.

## Expected Behavior

Small values (≤8 bytes) should be stored directly ("inline") in the key block entries instead of in a separate value block. This requires:

1. A new `EntryValue` variant for inline values
2. A constant defining the inline size threshold (8 bytes, matching the indirection overhead)
3. Writing logic: the builder must encode inline values with entry types 8+ (type = 8 + value_length)
4. Reading logic: the reader must decode inline entries and return the value directly from the key block data
5. A helper to compute value byte sizes for all entry types (replacing the per-type match arms in `get_key_entry`)
6. `ArcSlice` needs a method to create a sub-slice from a pointer into its backing data, for zero-copy access to inline values in key blocks

After implementing the code changes, update the crate's README to document the inline value format — the types 8..255 section should no longer say "future" and should describe the actual inline storage behavior.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/constants.rs` — value size constants
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST file writer, `EntryValue` enum, `KeyBlockBuilder`
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST file reader, entry type constants, key block parsing
- `turbopack/crates/turbo-persistence/src/collector_entry.rs` — collector entry value routing
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — lookup entry value routing
- `turbopack/crates/turbo-persistence/src/arc_slice.rs` — `ArcSlice` utility
- `turbopack/crates/turbo-persistence/README.md` — on-disk format documentation
