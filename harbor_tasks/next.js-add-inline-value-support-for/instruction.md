# Implement Inline Value Storage in SST Key Blocks

## Problem

The turbo-persistence crate's Static Sorted Table (SST) file format currently stores all values in separate value blocks, even when the value is very small (e.g., 1-8 bytes). For these tiny values, the 8 bytes of indirection metadata (block index, size, position) used to reference the value block is as large as or larger than the value itself. This wastes space and adds an unnecessary extra lookup on reads.

The key block entry type encoding already reserves types 8-255 for inline values (documented as "future" in the README), but the feature was never implemented — the code currently bails with an error for any entry type >= 8.

## Expected Behavior

Small values (≤8 bytes) should be stored directly ("inline") in the key block entries instead of in a separate value block. This requires:

1. A new `EntryValue::Inline` variant for inline values
2. A constant `MAX_INLINE_VALUE_SIZE` (value: 8) defining the inline size threshold, in `constants.rs`
3. A constant `KEY_BLOCK_ENTRY_TYPE_INLINE_MIN` (value: 8) for the minimum inline entry type tag, in `static_sorted_file.rs`
4. Writing logic: `KeyBlockBuilder` must have a `put_inline` method that encodes inline values with entry types 8+ (type = 8 + value_length), using `extend_from_slice` or `copy_from_slice` to write value data to the buffer
5. Reading logic: the `handle_key_match` function must handle inline entries by returning a `LookupValue::Slice` (using `slice_from_subslice`), not bailing with an error
6. An `entry_val_size` function in `static_sorted_file.rs` that computes the value byte size for all entry types, handling inline types via `ty >= KEY_BLOCK_ENTRY_TYPE_INLINE_MIN`
7. `ArcSlice` needs a `slice_from_subslice` method to create a sub-slice from a pointer into its backing data, for zero-copy access to inline values in key blocks

After implementing the code changes, update the crate's README to document the inline value format — the types 8..255 section should no longer say "future" and should describe the actual inline storage behavior.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/constants.rs` — value size constants, should define `MAX_INLINE_VALUE_SIZE = 8`
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — SST file writer, `EntryValue` enum (needs `Inline` variant), `KeyBlockBuilder` (needs `put_inline` method)
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — SST file reader, entry type constants (needs `KEY_BLOCK_ENTRY_TYPE_INLINE_MIN = 8`), key block parsing (needs `entry_val_size` function, `handle_key_match` must return `LookupValue::Slice` for inline types)
- `turbopack/crates/turbo-persistence/src/collector_entry.rs` — collector entry value routing
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — lookup entry value routing
- `turbopack/crates/turbo-persistence/src/arc_slice.rs` — `ArcSlice` utility (needs `slice_from_subslice` method)
- `turbopack/crates/turbo-persistence/README.md` — on-disk format documentation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
