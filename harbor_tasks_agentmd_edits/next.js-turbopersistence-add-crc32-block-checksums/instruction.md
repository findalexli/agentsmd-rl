# Add CRC32 block checksums to turbo-persistence

## Problem

The `turbo-persistence` crate (`turbopack/crates/turbo-persistence/`) stores cached data in SST (Static Sorted Table) files and blob files without any integrity verification. If a block gets corrupted on disk — from bit flips, partial writes, or filesystem issues — the system either silently returns wrong data or produces confusing LZ4 decompression failures with no indication of the root cause.

## Expected Behavior

Every block in SST files and every blob file should include a CRC32 checksum that is verified on read. When corruption is detected, the error should clearly identify which block and file is affected, for example: `"Cache corruption detected: checksum mismatch in block N of SST file seq:M"`.

Use the `crc32fast` crate for hardware-accelerated CRC32 computation.

## Scope

- Add a 4-byte CRC32 checksum field to the on-disk block header (expanding it from 4 to 8 bytes)
- Compute the checksum on the on-disk block data (after compression, if compressed)
- Verify the checksum on read before decompression
- All block types need checksums: value blocks, key blocks, and the index block
- Blob files also need a checksum in their header
- During compaction, medium values are copied as raw compressed blocks — their checksums should be carried through unchanged
- The `sst_inspect` binary should parse the new header and verify checksums

## Files to Look At

- `turbopack/crates/turbo-persistence/src/compression.rs` — compression helpers
- `turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs` — write path
- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — read path
- `turbopack/crates/turbo-persistence/src/write_batch.rs` — blob write
- `turbopack/crates/turbo-persistence/src/db.rs` — blob read
- `turbopack/crates/turbo-persistence/src/lookup_entry.rs` — compaction value carrier
- `turbopack/crates/turbo-persistence/src/lib.rs` — public exports
- `turbopack/crates/turbo-persistence/src/bin/sst_inspect.rs` — SST inspection tool

After implementing the code changes, make sure the crate's documentation accurately reflects the new on-disk format.
