# Fix mmap page alignment and improve error context in MetaFile::open_internal

## Bug Description

In `turbopack/crates/turbo-persistence/src/meta_file.rs`, `MmapOptions::offset()` requires the offset to be page-aligned (typically 4096 bytes), but the code passes `file.stream_position()` (the byte position after reading the variable-length header) as the mmap offset. This byte position is not guaranteed to be page-aligned, which causes `mmap` to fail or behave incorrectly on some inputs.

Additionally, error context is missing from several fallible operations in `open_internal` and `advise_mmap_for_persistence`, making it difficult to diagnose failures in production. The `?` operators in these functions do not attach context strings explaining what operation failed.

## What to Fix

### mmap fix (`meta_file.rs`):
1. Remove `options.offset(offset)` — map the entire file from byte 0 instead of trying to offset past the header
2. Add a new `amqf_data_start: usize` field to the `MetaFile` struct, storing the header-end byte offset
3. Change `amqf_data()` to return `&self.mmap[self.amqf_data_start..]` instead of `&self.mmap`, so only the AMQF data region is exposed. All existing callers that index into `amqf_data()` continue to work unchanged since their offsets are relative to the start of AMQF data.

### Error context (`meta_file.rs`):
- Add `.context("Failed to open meta file")` to `File::open(path)?`
- Add `.context("Failed to get stream position")` to `file.stream_position()?`
- Change the mmap context to `.context("Failed to mmap")`
- Add `.context("Failed to advise mmap")` to `mmap.advise(Advice::Random)?`

### Error context (`mmap_helper.rs`):
- Add `use anyhow::Context;` import
- Add `.context("Failed to advise mmap DontFork")` and `.context("Failed to advise mmap Unmergeable")`

## Affected Code

- `turbopack/crates/turbo-persistence/src/meta_file.rs`
- `turbopack/crates/turbo-persistence/src/mmap_helper.rs`

## Acceptance Criteria

- The mmap is created without a byte offset, mapping from the start of the file
- A new `amqf_data_start` field stores the header end position
- `amqf_data()` returns a slice starting at `amqf_data_start`
- All fallible operations in `open_internal` have error context
- `mmap_helper.rs` has error context on the advise calls
- Both files remain valid Rust
