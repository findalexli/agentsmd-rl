#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'struct ArcBlockCacheReader' turbopack/crates/turbo-persistence/src/static_sorted_file.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
index c14063deea35c2..6679b6a1be1643 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
@@ -1,4 +1,14 @@
-use std::{cmp::Ordering, fs::File, hash::BuildHasherDefault, path::Path, rc::Rc, sync::Arc};
+use std::{
+    cmp::Ordering,
+    fs::File,
+    hash::BuildHasherDefault,
+    path::Path,
+    rc::Rc,
+    sync::{
+        Arc,
+        atomic::{AtomicU64, Ordering as AtomicOrdering},
+    },
+};

 use anyhow::{Context, Result, bail, ensure};
 use memmap2::Mmap;
@@ -77,9 +87,12 @@ pub struct BlockWeighter;
 impl quick_cache::Weighter<(u32, u16), ArcBytes> for BlockWeighter {
     fn weight(&self, _key: &(u32, u16), val: &ArcBytes) -> u64 {
         if val.is_mmap_backed() {
-            // Mmap-backed blocks are cheap (just a pointer + Arc clone), so we
-            // assign a small fixed weight. Caching them avoids re-parsing block
-            // offsets on every lookup.
+            // Mmap-backed blocks bypass the cache (served directly from mmap),
+            // so this branch should never be reached.
+            debug_assert!(
+                !val.is_mmap_backed(),
+                "mmap-backed block should not be inserted into BlockCache"
+            );
             64
         } else {
             val.len() as u64 + 8
@@ -105,25 +118,24 @@ trait ValueBlockCache<B: SharedBytes> {
     ) -> Result<B>;
 }

-/// Lookup-path: concurrent `BlockCache`.
-impl ValueBlockCache<ArcBytes> for &BlockCache {
+/// Bundles the shared block cache with the per-file CRC-verified bitmap,
+/// used on the lookup path.
+#[derive(Clone, Copy)]
+struct ArcBlockCacheReader<'a> {
+    cache: &'a BlockCache,
+    verified_blocks: &'a [AtomicU64],
+}
+
+/// Lookup-path: concurrent `BlockCache` with uncompressed-bypass and
+/// once-per-block CRC verification via `verified_blocks` bitmap.
+impl ValueBlockCache<ArcBytes> for ArcBlockCacheReader<'_> {
     fn get_or_read(
         self,
         mmap: &Arc<Mmap>,
         meta: &StaticSortedFileMetaData,
         block_index: u16,
     ) -> Result<ArcBytes> {
-        Ok(
-            match self.get_value_or_guard(&(meta.sequence_number, block_index), None) {
-                GuardResult::Value(block) => block,
-                GuardResult::Guard(guard) => {
-                    let block: ArcBytes = read_block_generic(mmap, meta, block_index)?;
-                    let _ = guard.insert(block.clone());
-                    block
-                }
-                GuardResult::Timeout => unreachable!(),
-            },
-        )
+        get_or_cache_block(mmap, meta, block_index, self.cache, self.verified_blocks)
     }
 }

@@ -169,6 +181,11 @@ pub struct StaticSortedFile {
     /// We store as an Arc so we can hand out references (via ArcBytes) that can outlive this
     /// struct (not that we expect them to outlive it by very much)
     mmap: Arc<Mmap>,
+    /// One bit per block, set when that block's CRC has been verified at least once.
+    /// Uncompressed (mmap-backed) blocks bypass the `BlockCache`, so without this
+    /// bitmap the CRC would be re-computed on every access. `Relaxed` ordering
+    /// suffices: racing first-time verifications are idempotent.
+    verified_blocks: Box<[AtomicU64]>,
 }

 impl StaticSortedFile {
@@ -193,9 +210,14 @@ impl StaticSortedFile {
             let _ = mmap.advise_range(memmap2::Advice::Sequential, offset, mmap.len() - offset);
         }
         advise_mmap_for_persistence(&mmap)?;
+        let bitmap_words = (meta.block_count as usize).div_ceil(u64::BITS as usize);
+        let verified_blocks = (0..bitmap_words)
+            .map(|_| AtomicU64::new(0))
+            .collect::<Box<[_]>>();
         Ok(Self {
             meta,
             mmap: Arc::new(mmap),
+            verified_blocks,
         })
     }

@@ -214,21 +236,31 @@ impl StaticSortedFile {
         // There is exactly one index block per file (always the last block).
         // Read it first, then dispatch directly to the key block it points to.
         let index_block_index = self.meta.block_count - 1;
-        let index_block = self.get_key_block(index_block_index, key_block_cache)?;
+        let index_block = get_or_cache_block(
+            &self.mmap,
+            &self.meta,
+            index_block_index,
+            key_block_cache,
+            &self.verified_blocks,
+        )?;
         let key_block_index = self.lookup_index_block(&index_block, key_hash)?;

-        let key_block_arc = self.get_key_block(key_block_index, key_block_cache)?;
+        let key_block_arc = get_or_cache_block(
+            &self.mmap,
+            &self.meta,
+            key_block_index,
+            key_block_cache,
+            &self.verified_blocks,
+        )?;
+        let reader = ArcBlockCacheReader {
+            cache: value_block_cache,
+            verified_blocks: &self.verified_blocks,
+        };
         let block_type = be::read_u8(&key_block_arc);
         match block_type {
             BLOCK_TYPE_KEY_WITH_HASH | BLOCK_TYPE_KEY_NO_HASH => {
                 let has_hash = block_type == BLOCK_TYPE_KEY_WITH_HASH;
-                self.lookup_key_block::<K, FIND_ALL>(
-                    key_block_arc,
-                    key_hash,
-                    key,
-                    has_hash,
-                    value_block_cache,
-                )
+                self.lookup_key_block::<K, FIND_ALL>(key_block_arc, key_hash, key, has_hash, reader)
             }

             BLOCK_TYPE_FIXED_KEY_WITH_HASH | BLOCK_TYPE_FIXED_KEY_NO_HASH => {
@@ -238,7 +270,7 @@ impl StaticSortedFile {
                     key_hash,
                     key,
                     has_hash,
-                    value_block_cache,
+                    reader,
                 )
             }
             _ => {
@@ -279,7 +311,7 @@ impl StaticSortedFile {
         key_hash: u64,
         key: &K,
         has_hash: bool,
-        value_block_cache: &BlockCache,
+        reader: ArcBlockCacheReader<'_>,
     ) -> Result<SstLookupResult> {
         let hash_len: u8 = if has_hash { 8 } else { 0 };
         ensure!(block.len() >= 4, "key block too short");
@@ -292,14 +324,9 @@ impl StaticSortedFile {
         let offsets = &data[..entry_count * 4];
         let entries = &data[entry_count * 4..];

-        self.lookup_block_inner::<K, FIND_ALL>(
-            &block,
-            entry_count,
-            key_hash,
-            key,
-            value_block_cache,
-            |i| get_key_entry(offsets, entries, entry_count, i, hash_len),
-        )
+        self.lookup_block_inner::<K, FIND_ALL>(&block, entry_count, key_hash, key, reader, |i| {
+            get_key_entry(offsets, entries, entry_count, i, hash_len)
+        })
     }

     /// Looks up a key in a fixed-size key block.
@@ -312,7 +339,7 @@ impl StaticSortedFile {
         key_hash: u64,
         key: &K,
         has_hash: bool,
-        value_block_cache: &BlockCache,
+        reader: ArcBlockCacheReader<'_>,
     ) -> Result<SstLookupResult> {
         let hash_len: u8 = if has_hash { 8 } else { 0 };
         ensure!(block.len() >= 6, "fixed key block too short");
@@ -327,18 +354,11 @@ impl StaticSortedFile {
             "fixed key block for {entry_count} entries must is the wrong size"
         );

-        self.lookup_block_inner::<K, FIND_ALL>(
-            &block,
-            entry_count,
-            key_hash,
-            key,
-            value_block_cache,
-            |i| {
-                Ok(get_fixed_key_entry(
-                    entries, i, hash_len, key_size, value_type, stride,
-                ))
-            },
-        )
+        self.lookup_block_inner::<K, FIND_ALL>(&block, entry_count, key_hash, key, reader, |i| {
+            Ok(get_fixed_key_entry(
+                entries, i, hash_len, key_size, value_type, stride,
+            ))
+        })
     }

     /// Shared binary search + collection logic for both key block variants.
@@ -351,7 +371,7 @@ impl StaticSortedFile {
         entry_count: usize,
         key_hash: u64,
         key: &K,
-        value_block_cache: &BlockCache,
+        reader: ArcBlockCacheReader<'_>,
         get_entry: impl Fn(usize) -> Result<GetKeyEntryResult<'a>>,
     ) -> Result<SstLookupResult> {
         let mut l = 0;
@@ -374,7 +394,7 @@ impl StaticSortedFile {
                     if !FIND_ALL {
                         // SingleValue mode: each key has exactly one entry
                         // this is enforced when writing
-                        let result = self.handle_key_match(ty, val, block, value_block_cache)?;
+                        let result = self.handle_key_match(ty, val, block, reader)?;
                         return Ok(SstLookupResult::Found(SmallVec::from_buf([result])));
                     }
                     // FIND_ALL (MultiValue) mode: collect all values for this key.
@@ -393,7 +413,7 @@ impl StaticSortedFile {
                         if !entry_matches_key(hash, entry_key, key_hash, key) {
                             break;
                         }
-                        results.push(self.handle_key_match(ty, val, block, value_block_cache)?);
+                        results.push(self.handle_key_match(ty, val, block, reader)?);
                     }
                     // Technically we could `.reverse()` the items collected by the backwards
                     // scan, but the only ordering constraint we need to maintain for single
@@ -403,7 +423,7 @@ impl StaticSortedFile {
                     // their order.

                     // Add the entry at `m`
-                    results.push(self.handle_key_match(ty, val, block, value_block_cache)?);
+                    results.push(self.handle_key_match(ty, val, block, reader)?);
                     for i in (m + 1)..r {
                         let GetKeyEntryResult {
                             hash,
@@ -414,7 +434,7 @@ impl StaticSortedFile {
                         if !entry_matches_key(hash, entry_key, key_hash, key) {
                             break;
                         }
-                        results.push(self.handle_key_match(ty, val, block, value_block_cache)?);
+                        results.push(self.handle_key_match(ty, val, block, reader)?);
                     }
                     return Ok(SstLookupResult::Found(results));
                 }
@@ -431,44 +451,63 @@ impl StaticSortedFile {
         ty: u8,
         val: &[u8],
         key_block_arc: &ArcBytes,
-        value_block_cache: &BlockCache,
+        reader: ArcBlockCacheReader<'_>,
     ) -> Result<LookupValue> {
-        handle_key_match_generic(
-            &self.mmap,
-            &self.meta,
-            ty,
-            val,
-            key_block_arc,
-            value_block_cache,
-        )
+        handle_key_match_generic(&self.mmap, &self.meta, ty, val, key_block_arc, reader)
+}
+}

-    /// Gets a key block from the cache or reads it from the file.
-    fn get_key_block(
-        &self,
-        block: u16,
-        key_block_cache: &BlockCache,
-    ) -> Result<ArcBytes, anyhow::Error> {
-        Ok(
-            match key_block_cache.get_value_or_guard(&(self.meta.sequence_number, block), None) {
-                GuardResult::Value(block) => block,
-                GuardResult::Guard(guard) => {
-                    let block = self.read_block(block)?;
-                    let _ = guard.insert(block.clone());
-                    block
-                }
-                GuardResult::Timeout => unreachable!(),
-            },
-        )
-    }
+/// Gets a block from the cache, or reads it from the mmap and inserts it.
+///
+/// Reads the block header exactly once via `get_raw_block_slice` (which
+/// includes all `strict_checks` bounds guards). Uncompressed blocks bypass
+/// the cache — an mmap-backed `ArcBytes` is cheaper than a cache lookup.
+/// Their CRC is verified at most once per file open, tracked by
+/// `verified_blocks`. Compressed blocks are looked up in `cache`; on a
+/// miss they are decompressed, CRC-verified, and inserted.
+fn get_or_cache_block(
+    mmap: &Arc<Mmap>,
+    meta: &StaticSortedFileMetaData,
+    block_index: u16,
+    cache: &BlockCache,
+    verified_blocks: &[AtomicU64],
+) -> Result<ArcBytes> {
+    let (uncompressed_length, checksum, block_data) = get_raw_block_slice(mmap, meta, block_index)
+        .with_context(|| {
+            format!(
+                "Failed to read raw block {} from {:08}.sst",
+                block_index, meta.sequence_number
+            )
+        })?;

-    /// Reads a block from the file, decompressing if needed, and verifies its checksum.
-    ///
-    /// The checksum is verified on the raw on-disk data **before** decompression, so
-    /// corruption is caught before passing data to LZ4.
-    fn read_block(&self, block_index: u16) -> Result<ArcBytes> {
-        read_block_generic(&self.mmap, &self.meta, block_index)
+    if uncompressed_length == 0 {
+        // Uncompressed: serve directly from mmap. Verify CRC only once per file open.
+        verify_checksum_once(meta, block_data, checksum, block_index, verified_blocks)?;
+        // SAFETY: block_data points into the mmap backing `mmap`.
+        return Ok(unsafe { ArcBytes::from_mmap(mmap, block_data) });
     }
+
+    // Compressed: check cache; decompress and insert on miss.
+    Ok(
+        match cache.get_value_or_guard(&(meta.sequence_number, block_index), None) {
+            GuardResult::Value(block) => block,
+            GuardResult::Guard(guard) => {
+                // A cached block may have been evicted, so re-reading still
+                // benefits from the bitmap to skip redundant CRC verification.
+                verify_checksum_once(meta, block_data, checksum, block_index, verified_blocks)?;
+                let block = ArcBytes::from_decompressed(uncompressed_length, block_data)
+                    .with_context(|| {
+                        format!(
+                            "Failed to decompress block {} from {:08}.sst ({} bytes uncompressed)",
+                            block_index, meta.sequence_number, uncompressed_length
+                        )
+                    })?;
+                let _ = guard.insert(block.clone());
+                block
+            }
+            GuardResult::Timeout => unreachable!(),
+        },
+    )
 }

 /// Gets the raw block slice directly from a memory-mapped file.
@@ -552,6 +591,29 @@ fn verify_checksum(
     Ok(())
 }

+/// Verifies a block's CRC using the `verified_blocks` bitmap to avoid redundant
+/// work. In practice each block is verified once, but concurrent first-time
+/// accesses may race and verify the same block more than once — this is harmless
+/// since the check is deterministic and idempotent. Verification failures are
+/// *not* recorded in the bitmap, so a corrupted block will be re-checked (and
+/// fail again) on every access.
+fn verify_checksum_once(
+    meta: &StaticSortedFileMetaData,
+    data: &[u8],
+    expected: u32,
+    block_index: u16,
+    verified_blocks: &[AtomicU64],
+) -> Result<()> {
+    let word_idx = block_index as usize / u64::BITS as usize;
+    let bit = 1u64 << (block_index as usize % u64::BITS as usize);
+    if verified_blocks[word_idx].load(AtomicOrdering::Relaxed) & bit != 0 {
+        return Ok(());
+    }
+    verify_checksum(meta, data, expected, block_index)?;
+    verified_blocks[word_idx].fetch_or(bit, AtomicOrdering::Relaxed);
+    Ok(())
+}
+
 /// Returns `(uncompressed_length, checksum, block)` wrapping the raw on-disk
 /// data as the given byte type. Generic over `ArcBytes`/`RcBytes`.
 fn get_raw_block_generic<B: SharedBytes>(

PATCH

echo "Patch applied successfully."
