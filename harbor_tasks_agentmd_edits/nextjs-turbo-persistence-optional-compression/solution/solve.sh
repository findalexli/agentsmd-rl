#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'CompressionConfig' turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/README.md b/turbopack/crates/turbo-persistence/README.md
index 9c49c829196692..1b36cf853e72cd 100644
--- a/turbopack/crates/turbo-persistence/README.md
+++ b/turbopack/crates/turbo-persistence/README.md
@@ -79,11 +79,18 @@ The SST file contains only data without any header.
 
 - serialized key Compression Dictionary
 - foreach block
-  - 4 bytes uncompressed block length
-  - compressed data
+  - 4 bytes block header (uncompressed length or sentinel)
+  - block data (compressed or uncompressed)
 - foreach block
   - 4 bytes end of block offset relative to start of all blocks
 
+#### Block Compression
+
+Blocks can be stored compressed (LZ4) or uncompressed. The 4-byte header distinguishes them:
+
+- **Header > 0**: Block is LZ4 compressed. Header value is the uncompressed length.
+- **Header = 0**: Block is stored uncompressed. Actual length is derived from block offsets.
+
 #### Index Block
 
 - 1 byte block type (0: index block)
diff --git a/turbopack/crates/turbo-persistence/benches/mod.rs b/turbopack/crates/turbo-persistence/benches/mod.rs
index 8b7e2c181deb7d..3e9576bf95f1f7 100644
--- a/turbopack/crates/turbo-persistence/benches/mod.rs
+++ b/turbopack/crates/turbo-persistence/benches/mod.rs
@@ -10,7 +10,7 @@ use quick_cache::sync::GuardResult;
 use rand::{Rng, SeedableRng, rngs::SmallRng, seq::SliceRandom};
 use tempfile::TempDir;
 use turbo_persistence::{
-    ArcSlice, BlockCache, CompactConfig, Entry, EntryValue, MetaEntryFlags, SerialScheduler,
+    ArcBytes, BlockCache, CompactConfig, Entry, EntryValue, MetaEntryFlags, SerialScheduler,
     StaticSortedFile, StaticSortedFileMetaData, TurboPersistence, hash_key,
     write_static_stored_file,
 };
@@ -957,7 +957,7 @@ fn bench_block_cache(c: &mut Criterion) {
 
             let mut block_data = vec![0u8; BLOCK_SIZE];
             rng.fill(&mut block_data[..]);
-            let block = ArcSlice::from(block_data.into_boxed_slice());
+            let block = ArcBytes::from(block_data.into_boxed_slice());
 
             // Create cache with enough capacity for all entries
             let cache: BlockCache = BlockCache::with(
diff --git a/turbopack/crates/turbo-persistence/src/arc_bytes.rs b/turbopack/crates/turbo-persistence/src/arc_bytes.rs
new file mode 100644
index 00000000000000..df3ac1547cf346
--- /dev/null
+++ b/turbopack/crates/turbo-persistence/src/arc_bytes.rs
@@ -0,0 +1,154 @@
+use std::{
+    borrow::Borrow,
+    fmt::{self, Debug, Formatter},
+    hash::{Hash, Hasher},
+    io::{self, Read},
+    ops::{Deref, Range},
+    sync::Arc,
+};
+
+use memmap2::Mmap;
+
+/// The backing storage for an `ArcBytes`.
+///
+/// The inner values are never read directly — they exist solely to keep the
+/// backing memory alive while the raw `data` pointer in `ArcBytes` references it.
+#[derive(Clone)]
+enum Backing {
+    Arc { _backing: Arc<[u8]> },
+    Mmap { _backing: Arc<Mmap> },
+}
+
+/// An owned byte slice backed by either an `Arc<[u8]>` or a memory-mapped file.
+#[derive(Clone)]
+pub struct ArcBytes {
+    data: *const [u8],
+    backing: Backing,
+}
+
+unsafe impl Send for ArcBytes {}
+unsafe impl Sync for ArcBytes {}
+
+impl From<Arc<[u8]>> for ArcBytes {
+    fn from(arc: Arc<[u8]>) -> Self {
+        Self {
+            data: &*arc as *const [u8],
+            backing: Backing::Arc { _backing: arc },
+        }
+    }
+}
+
+impl From<Box<[u8]>> for ArcBytes {
+    fn from(b: Box<[u8]>) -> Self {
+        Self::from(Arc::from(b))
+    }
+}
+
+impl Deref for ArcBytes {
+    type Target = [u8];
+
+    fn deref(&self) -> &Self::Target {
+        unsafe { &*self.data }
+    }
+}
+
+impl Borrow<[u8]> for ArcBytes {
+    fn borrow(&self) -> &[u8] {
+        self
+    }
+}
+
+impl Hash for ArcBytes {
+    fn hash<H: Hasher>(&self, state: &mut H) {
+        self.deref().hash(state)
+    }
+}
+
+impl PartialEq for ArcBytes {
+    fn eq(&self, other: &Self) -> bool {
+        self.deref().eq(other.deref())
+    }
+}
+
+impl Debug for ArcBytes {
+    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
+        Debug::fmt(&**self, f)
+    }
+}
+
+impl Eq for ArcBytes {}
+
+impl Read for ArcBytes {
+    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
+        let available = &**self;
+        let len = std::cmp::min(buf.len(), available.len());
+        buf[..len].copy_from_slice(&available[..len]);
+        // Advance the slice view
+        self.data = &available[len..] as *const [u8];
+        Ok(len)
+    }
+}
+
+/// Returns `true` if `subslice` lies entirely within `backing`.
+fn is_subslice_of(subslice: &[u8], backing: &[u8]) -> bool {
+    let backing = backing.as_ptr_range();
+    let sub = subslice.as_ptr_range();
+    sub.start >= backing.start && sub.end <= backing.end
+}
+
+impl ArcBytes {
+    /// Returns a new `ArcBytes` that points to a sub-range of the current slice.
+    pub fn slice(self, range: Range<usize>) -> ArcBytes {
+        let data = &*self;
+        let data = &data[range] as *const [u8];
+        Self {
+            data,
+            backing: self.backing,
+        }
+    }
+
+    /// Creates a sub-slice from a slice reference that points into this ArcBytes' backing data.
+    ///
+    /// # Safety
+    ///
+    /// The caller must ensure that `subslice` points to memory within this ArcBytes'
+    /// backing storage (not just within the current slice view, but anywhere in the original
+    /// backing data).
+    pub unsafe fn slice_from_subslice(&self, subslice: &[u8]) -> ArcBytes {
+        debug_assert!(
+            is_subslice_of(
+                subslice,
+                match &self.backing {
+                    Backing::Arc { _backing } => _backing,
+                    Backing::Mmap { _backing } => _backing,
+                }
+            ),
+            "slice_from_subslice: subslice is not within the backing storage"
+        );
+        Self {
+            data: subslice as *const [u8],
+            backing: self.backing.clone(),
+        }
+    }
+
+    /// Creates an `ArcBytes` backed by a memory-mapped file.
+    ///
+    /// # Safety
+    ///
+    /// The caller must ensure that `subslice` points to memory within the given `mmap`.
+    pub unsafe fn from_mmap(mmap: Arc<Mmap>, subslice: &[u8]) -> ArcBytes {
+        debug_assert!(
+            is_subslice_of(subslice, &mmap),
+            "from_mmap: subslice is not within the mmap"
+        );
+        ArcBytes {
+            data: subslice as *const [u8],
+            backing: Backing::Mmap { _backing: mmap },
+        }
+    }
+
+    /// Returns `true` if this `ArcBytes` is backed by a memory-mapped file.
+    pub fn is_mmap_backed(&self) -> bool {
+        matches!(self.backing, Backing::Mmap { .. })
+    }
+}
diff --git a/turbopack/crates/turbo-persistence/src/arc_slice.rs b/turbopack/crates/turbo-persistence/src/arc_slice.rs
deleted file mode 100644
index 721aab96da9309..00000000000000
--- a/turbopack/crates/turbo-persistence/src/arc_slice.rs
+++ /dev/null
@@ -1,103 +0,0 @@
-use std::{
-    borrow::Borrow,
-    fmt::{self, Debug, Formatter},
-    hash::{Hash, Hasher},
-    io::{self, Read},
-    ops::{Deref, Range},
-    sync::Arc,
-};
-
-/// A owned slice that is backed by an `Arc`.
-#[derive(Clone)]
-pub struct ArcSlice<T> {
-    data: *const [T],
-    arc: Arc<[T]>,
-}
-
-unsafe impl<T> Send for ArcSlice<T> {}
-unsafe impl<T> Sync for ArcSlice<T> {}
-
-impl<T> From<Arc<[T]>> for ArcSlice<T> {
-    fn from(arc: Arc<[T]>) -> Self {
-        Self {
-            data: &*arc as *const [T],
-            arc,
-        }
-    }
-}
-
-impl<T> From<Box<[T]>> for ArcSlice<T> {
-    fn from(b: Box<[T]>) -> Self {
-        Self::from(Arc::from(b))
-    }
-}
-
-impl<T> Deref for ArcSlice<T> {
-    type Target = [T];
-
-    fn deref(&self) -> &Self::Target {
-        unsafe { &*self.data }
-    }
-}
-
-impl<T> Borrow<[T]> for ArcSlice<T> {
-    fn borrow(&self) -> &[T] {
-        self
-    }
-}
-
-impl<T: Hash> Hash for ArcSlice<T> {
-    fn hash<H: Hasher>(&self, state: &mut H) {
-        self.deref().hash(state)
-    }
-}
-
-impl<T: PartialEq> PartialEq for ArcSlice<T> {
-    fn eq(&self, other: &Self) -> bool {
-        self.deref().eq(other.deref())
-    }
-}
-
-impl<T: Debug> Debug for ArcSlice<T> {
-    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
-        Debug::fmt(&**self, f)
-    }
-}
-
-impl<T: Eq> Eq for ArcSlice<T> {}
-
-impl Read for ArcSlice<u8> {
-    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
-        let available = &**self;
-        let len = std::cmp::min(buf.len(), available.len());
-        buf[..len].copy_from_slice(&available[..len]);
-        // Advance the slice view
-        self.data = &available[len..] as *const [u8];
-        Ok(len)
-    }
-}
-
-impl<T> ArcSlice<T> {
-    /// Returns a new `ArcSlice` that points to a slice of the current slice.
-    pub fn slice(self, range: Range<usize>) -> ArcSlice<T> {
-        let data = &*self;
-        let data = &data[range] as *const [T];
-        Self {
-            data,
-            arc: self.arc,
-        }
-    }
-
-    /// Creates a sub-slice from a slice reference that points into this ArcSlice's backing data.
-    ///
-    /// # Safety
-    ///
-    /// The caller must ensure that `subslice` points to memory within this ArcSlice's
-    /// backing Arc (not just within the current slice view, but anywhere in the original Arc).
-    pub unsafe fn slice_from_subslice(&self, subslice: &[T]) -> ArcSlice<T> {
-        Self {
-            data: subslice as *const [T],
-            arc: self.arc.clone(),
-        }
-    }
-}
diff --git a/turbopack/crates/turbo-persistence/src/compression.rs b/turbopack/crates/turbo-persistence/src/compression.rs
index adfa37017ce039..017370762b7d2c 100644
--- a/turbopack/crates/turbo-persistence/src/compression.rs
+++ b/turbopack/crates/turbo-persistence/src/compression.rs
@@ -3,12 +3,22 @@ use std::{mem::MaybeUninit, sync::Arc};
 use anyhow::{Context, Result};
 use lzzzz::lz4::{ACC_LEVEL_DEFAULT, decompress, decompress_with_dict};
 
+/// Decompresses a block into an Arc allocation.
+///
+/// The caller must ensure `uncompressed_length > 0` (i.e., the block is actually compressed).
+/// Uncompressed blocks should be handled via zero-copy mmap slices before calling this.
 pub fn decompress_into_arc(
     uncompressed_length: u32,
     block: &[u8],
     compression_dictionary: Option<&[u8]>,
     _long_term: bool,
 ) -> Result<Arc<[u8]>> {
+    debug_assert!(
+        uncompressed_length > 0,
+        "decompress_into_arc called with uncompressed_length=0; uncompressed blocks should use \
+         zero-copy mmap path"
+    );
+
     // We directly allocate the buffer in an Arc to avoid copying it into an Arc and avoiding
     // double indirection. This is a dynamically sized arc.
     let buffer: Arc<[MaybeUninit<u8>]> = Arc::new_zeroed_slice(uncompressed_length as usize);
diff --git a/turbopack/crates/turbo-persistence/src/db.rs b/turbopack/crates/turbo-persistence/src/db.rs
index a677f6a6b9f24d..3d223d27574003 100644
--- a/turbopack/crates/turbo-persistence/src/db.rs
+++ b/turbopack/crates/turbo-persistence/src/db.rs
@@ -21,7 +21,7 @@ use smallvec::SmallVec;
 pub use crate::compaction::selector::CompactConfig;
 use crate::{
     QueryKey,
-    arc_slice::ArcSlice,
+    arc_bytes::ArcBytes,
     compaction::selector::{Compactable, get_merge_segments},
     compression::decompress_into_arc,
     constants::{
@@ -377,7 +377,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
 
     /// Reads and decompresses a blob file. This is not backed by any cache.
     #[tracing::instrument(level = "info", name = "reading database blob", skip_all)]
-    fn read_blob(&self, seq: u32) -> Result<ArcSlice<u8>> {
+    fn read_blob(&self, seq: u32) -> Result<ArcBytes> {
         let path = self.path.join(format!("{seq:08}.blob"));
         let mmap = unsafe { Mmap::map(&File::open(&path)?)? };
         #[cfg(unix)]
@@ -392,7 +392,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
         let uncompressed_length = compressed.read_u32::<BE>()?;
 
         let buffer = decompress_into_arc(uncompressed_length, compressed, None, true)?;
-        Ok(ArcSlice::from(buffer))
+        Ok(ArcBytes::from(buffer))
     }
 
     /// Returns true if the database is empty.
@@ -1357,7 +1357,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
 
     /// Get a value from the database. Returns None if the key is not found. The returned value
     /// might hold onto a block of the database and it should not be hold long-term.
-    pub fn get<K: QueryKey>(&self, family: usize, key: &K) -> Result<Option<ArcSlice<u8>>> {
+    pub fn get<K: QueryKey>(&self, family: usize, key: &K) -> Result<Option<ArcBytes>> {
         debug_assert!(family < FAMILIES, "Family index out of bounds");
         let span = tracing::trace_span!(
             "database read",
@@ -1429,7 +1429,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
         &self,
         family: usize,
         keys: &[K],
-    ) -> Result<Vec<Option<ArcSlice<u8>>>> {
+    ) -> Result<Vec<Option<ArcBytes>>> {
         debug_assert!(family < FAMILIES, "Family index out of bounds");
         let span = tracing::trace_span!(
             "database batch read",
diff --git a/turbopack/crates/turbo-persistence/src/lib.rs b/turbopack/crates/turbo-persistence/src/lib.rs
index fd17c20c564499..51b5d096d0e529 100644
--- a/turbopack/crates/turbo-persistence/src/lib.rs
+++ b/turbopack/crates/turbo-persistence/src/lib.rs
@@ -3,7 +3,7 @@
 #![feature(sync_unsafe_cell)]
 #![feature(iter_collect_into)]
 
-mod arc_slice;
+mod arc_bytes;
 mod collector;
 mod collector_entry;
 mod compaction;
@@ -26,7 +26,7 @@ mod write_batch;
 #[cfg(test)]
 mod tests;
 
-pub use arc_slice::ArcSlice;
+pub use arc_bytes::ArcBytes;
 pub use db::{CompactConfig, MetaFileEntryInfo, MetaFileInfo, TurboPersistence};
 pub use key::{KeyBase, QueryKey, StoreKey, hash_key};
 pub use meta_file::MetaEntryFlags;
diff --git a/turbopack/crates/turbo-persistence/src/lookup_entry.rs b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
index da1c5fa7ebb119..2322aaa25be195 100644
--- a/turbopack/crates/turbo-persistence/src/lookup_entry.rs
+++ b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
@@ -1,5 +1,5 @@
 use crate::{
-    ArcSlice,
+    ArcBytes,
     constants::{MAX_INLINE_VALUE_SIZE, MAX_SMALL_VALUE_SIZE},
     static_sorted_file_builder::{Entry, EntryValue},
 };
@@ -10,8 +10,8 @@ pub enum LookupValue {
     Deleted,
     /// The value is stored in the SST file.
     ///
-    /// The ArcSlice will be pointing either at a keyblock or a value block in the SST
-    Slice { value: ArcSlice<u8> },
+    /// The ArcBytes will be pointing either at a keyblock or a value block in the SST
+    Slice { value: ArcBytes },
     /// The value is stored in a blob file.
     Blob { sequence_number: u32 },
 }
@@ -35,8 +35,15 @@ impl LazyLookupValue<'_> {
             LazyLookupValue::Eager(LookupValue::Deleted) => 0,
             LazyLookupValue::Eager(LookupValue::Blob { .. }) => 0,
             LazyLookupValue::Medium {
-                uncompressed_size, ..
-            } => *uncompressed_size as usize,
+                uncompressed_size,
+                block,
+            } => {
+                if *uncompressed_size == 0 {
+                    block.len()
+                } else {
+                    *uncompressed_size as usize
+                }
+            }
         }
     }
 
@@ -71,7 +78,7 @@ pub struct LookupEntry<'l> {
     /// The hash of the key.
     pub hash: u64,
     /// The key.
-    pub key: ArcSlice<u8>,
+    pub key: ArcBytes,
     /// The value.
     pub value: LazyLookupValue<'l>,
 }
@@ -107,7 +114,7 @@ impl Entry for LookupEntry<'_> {
             LazyLookupValue::Medium {
                 uncompressed_size,
                 block,
-            } => EntryValue::MediumCompressed {
+            } => EntryValue::MediumRaw {
                 uncompressed_size: *uncompressed_size,
                 block,
             },
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
index 6d8533a551b99d..3d1e50cd997a01 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
@@ -4,6 +4,7 @@ use std::{
     hash::BuildHasherDefault,
     ops::Range,
     path::{Path, PathBuf},
+    sync::Arc,
 };
 
 use anyhow::{Context, Result, bail};
@@ -14,7 +15,7 @@ use rustc_hash::FxHasher;
 
 use crate::{
     QueryKey,
-    arc_slice::ArcSlice,
+    arc_bytes::ArcBytes,
     compression::decompress_into_arc,
     constants::MAX_INLINE_VALUE_SIZE,
     lookup_entry::{LazyLookupValue, LookupEntry, LookupValue},
@@ -62,14 +63,21 @@ impl From<LookupValue> for SstLookupResult {
 #[derive(Clone, Default)]
 pub struct BlockWeighter;
 
-impl quick_cache::Weighter<(u32, u16), ArcSlice<u8>> for BlockWeighter {
-    fn weight(&self, _key: &(u32, u16), val: &ArcSlice<u8>) -> u64 {
-        val.len() as u64 + 8
+impl quick_cache::Weighter<(u32, u16), ArcBytes> for BlockWeighter {
+    fn weight(&self, _key: &(u32, u16), val: &ArcBytes) -> u64 {
+        if val.is_mmap_backed() {
+            // Mmap-backed blocks are cheap (just a pointer + Arc clone), so we
+            // assign a small fixed weight. Caching them avoids re-parsing block
+            // offsets on every lookup.
+            64
+        } else {
+            val.len() as u64 + 8
+        }
     }
 }
 
 pub type BlockCache =
-    quick_cache::sync::Cache<(u32, u16), ArcSlice<u8>, BlockWeighter, BuildHasherDefault<FxHasher>>;
+    quick_cache::sync::Cache<(u32, u16), ArcBytes, BlockWeighter, BuildHasherDefault<FxHasher>>;
 
 #[derive(Clone, Debug)]
 pub struct StaticSortedFileMetaData {
@@ -104,7 +112,9 @@ pub struct StaticSortedFile {
     /// The meta file of this file.
     meta: StaticSortedFileMetaData,
     /// The memory mapped file.
-    mmap: Mmap,
+    /// We store as an Arc so we can hand out references (via ArcBytes) that can outlive this
+    /// struct (not that we expect them to outlive it by very much)
+    mmap: Arc<Mmap>,
 }
 
 impl StaticSortedFile {
@@ -126,7 +136,10 @@ impl StaticSortedFile {
             let offset = meta.block_offsets_start(mmap.len());
             let _ = mmap.advise_range(memmap2::Advice::Sequential, offset, mmap.len() - offset);
         }
-        let file = Self { meta, mmap };
+        let file = Self {
+            meta,
+            mmap: Arc::new(mmap),
+        };
         Ok(file)
     }
 
@@ -229,7 +242,7 @@ impl StaticSortedFile {
     /// Looks up a key in a key block and the value in a value block.
     fn lookup_key_block<K: QueryKey>(
         &self,
-        mut block: ArcSlice<u8>,
+        mut block: ArcBytes,
         key_hash: u64,
         key: &K,
         has_hash: bool,
@@ -276,7 +289,7 @@ impl StaticSortedFile {
         &self,
         ty: u8,
         mut val: &[u8],
-        key_block_arc: &ArcSlice<u8>,
+        key_block_arc: &ArcBytes,
         value_block_cache: &BlockCache,
     ) -> Result<LookupValue> {
         Ok(match ty {
@@ -285,7 +298,7 @@ impl StaticSortedFile {
                 let size = val.read_u16::<BE>()? as usize;
                 let position = val.read_u32::<BE>()? as usize;
                 let value = self
-                    .get_value_block(block, value_block_cache)?
+                    .get_small_value_block(block, value_block_cache)?
                     .slice(position..position + size);
                 LookupValue::Slice { value }
             }
@@ -313,7 +326,7 @@ impl StaticSortedFile {
         &self,
         block: u16,
         key_block_cache: &BlockCache,
-    ) -> Result<ArcSlice<u8>, anyhow::Error> {
+    ) -> Result<ArcBytes, anyhow::Error> {
         Ok(
             match key_block_cache.get_value_or_guard(&(self.meta.sequence_number, block), None) {
                 GuardResult::Value(block) => block,
@@ -328,7 +341,11 @@ impl StaticSortedFile {
     }
 
     /// Gets a value block from the cache or reads it from the file.
-    fn get_value_block(&self, block: u16, value_block_cache: &BlockCache) -> Result<ArcSlice<u8>> {
+    fn get_small_value_block(
+        &self,
+        block: u16,
+        value_block_cache: &BlockCache,
+    ) -> Result<ArcBytes> {
         let block =
             match value_block_cache.get_value_or_guard(&(self.meta.sequence_number, block), None) {
                 GuardResult::Value(block) => block,
@@ -343,7 +360,7 @@ impl StaticSortedFile {
     }
 
     /// Reads a key block from the file.
-    fn read_key_block(&self, block_index: u16) -> Result<ArcSlice<u8>> {
+    fn read_key_block(&self, block_index: u16) -> Result<ArcBytes> {
         self.read_block(
             block_index,
             Some(&self.mmap[self.meta.key_compression_dictionary_range()]),
@@ -352,12 +369,12 @@ impl StaticSortedFile {
     }
 
     /// Reads a value block from the file.
-    fn read_small_value_block(&self, block_index: u16) -> Result<ArcSlice<u8>> {
+    fn read_small_value_block(&self, block_index: u16) -> Result<ArcBytes> {
         self.read_block(block_index, None, false)
     }
 
     /// Reads a value block from the file.
-    fn read_value_block(&self, block_index: u16) -> Result<ArcSlice<u8>> {
+    fn read_value_block(&self, block_index: u16) -> Result<ArcBytes> {
         self.read_block(block_index, None, true)
     }
 
@@ -368,8 +385,25 @@ impl StaticSortedFile {
         block_index: u16,
         compression_dictionary: Option<&[u8]>,
         long_term: bool,
-    ) -> Result<ArcSlice<u8>> {
-        let (uncompressed_length, block) = self.get_compressed_block(block_index)?;
+    ) -> Result<ArcBytes> {
+        let (uncompressed_length, block) = self.get_raw_block(block_index)?;
+
+        // 0 means the block was not compressed, just return the slice into the mmap
+        if uncompressed_length == 0 {
+            // SAFETY: get_raw_block only returns reference into the mmap.
+            return Ok(unsafe { ArcBytes::from_mmap(self.mmap.clone(), block) });
+        }
+
+        // Advise Sequential only here: we're about to linearly scan the block
+        // through the decompressor. For uncompressed blocks (returned above)
+        // and lazy medium values (which call get_raw_block directly without
+        // decompressing), the file-level Random advice applies.
+        #[cfg(unix)]
+        let _ = self.mmap.advise_range(
+            memmap2::Advice::Sequential,
+            block.as_ptr() as usize - self.mmap.as_ptr() as usize,
+            block.len(),
+        );
 
         let buffer = decompress_into_arc(
             uncompressed_length,
@@ -377,11 +411,11 @@ impl StaticSortedFile {
             compression_dictionary,
             long_term,
         )?;
-        Ok(ArcSlice::from(buffer))
+        Ok(ArcBytes::from(buffer))
     }
 
     /// Gets the slice of the compressed block from the memory mapped file.
-    fn get_compressed_block(&self, block_index: u16) -> Result<(u32, &[u8])> {
+    fn get_raw_block(&self, block_index: u16) -> Result<(u32, &[u8])> {
         #[cfg(feature = "strict_checks")]
         if block_index >= self.meta.block_count {
             bail!(
@@ -429,13 +463,8 @@ impl StaticSortedFile {
                 self.meta.blocks_start()
             );
         }
-        #[cfg(unix)]
-        let _ = self.mmap.advise_range(
-            memmap2::Advice::Sequential,
-            block_start,
-            block_end - block_start,
-        );
-        let uncompressed_length = (&self.mmap[block_start..block_start + 4]).read_u32::<BE>()?;
+        let uncompressed_length =
+            u32::from_be_bytes(self.mmap[block_start..block_start + 4].try_into()?);
         let block = &self.mmap[block_start + 4..block_end];
         Ok((uncompressed_length, block))
     }
@@ -452,15 +481,15 @@ pub struct StaticSortedFileIter<'l> {
 }
 
 struct CurrentKeyBlock {
-    offsets: ArcSlice<u8>,
-    entries: ArcSlice<u8>,
+    offsets: ArcBytes,
+    entries: ArcBytes,
     entry_count: usize,
     index: usize,
     hash_len: u8,
 }
 
 struct CurrentIndexBlock {
-    entries: ArcSlice<u8>,
+    entries: ArcBytes,
     block_indices_count: usize,
     index: usize,
 }
@@ -534,7 +563,7 @@ impl<'l> StaticSortedFileIter<'l> {
                 let value = if ty == KEY_BLOCK_ENTRY_TYPE_MEDIUM {
                     let mut val = val;
                     let block = val.read_u16::<BE>()?;
-                    let (uncompressed_size, block) = self.this.get_compressed_block(block)?;
+                    let (uncompressed_size, block) = self.this.get_raw_block(block)?;
                     LazyLookupValue::Medium {
                         uncompressed_size,
                         block,
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
index 3be860dfd307f0..4181ead2c5d294 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
@@ -79,8 +79,10 @@ pub enum EntryValue<'l> {
     Small { value: &'l [u8] },
     /// Medium-sized value. They are stored in their own value block.
     Medium { value: &'l [u8] },
-    /// Medium-sized value. They are stored in their own value block. Precompressed.
-    MediumCompressed {
+    /// Medium-sized value. They are stored in their own value block. In the raw form as on disk.
+    MediumRaw {
+        /// The uncompressed size of the block data. `0` means the block is stored uncompressed
+        /// (and thus the size is the `len` of the block)
         uncompressed_size: u32,
         block: &'l [u8],
     },
@@ -224,6 +226,16 @@ fn compute_key_compression_dictionary<E: Entry>(
     Ok(result)
 }
 
+enum CompressionConfig<'a> {
+    /// Attempt compression; use the result only if it's smaller than the original.
+    TryCompress {
+        dict: Option<&'a [u8]>,
+        long_term: bool,
+    },
+    /// Write the block uncompressed.
+    Uncompressed,
+}
+
 struct BlockWriter<'l> {
     buffer: &'l mut Vec<u8>,
     block_offsets: Vec<u32>,
@@ -255,32 +267,69 @@ impl<'l> BlockWriter<'l> {
 
     #[tracing::instrument(level = "trace", skip_all)]
     fn write_key_block(&mut self, block: &[u8], dict: &[u8]) -> Result<()> {
-        self.write_block(block, Some(dict), false)
-            .context("Failed to write key block")
+        self.write_block(
+            block,
+            CompressionConfig::TryCompress {
+                dict: Some(dict),
+                long_term: false,
+            },
+        )
+        .context("Failed to write key block")
     }
 
     #[tracing::instrument(level = "trace", skip_all)]
-    fn write_index_block(&mut self, block: &[u8], dict: &[u8]) -> Result<()> {
-        self.write_block(block, Some(dict), false)
+    fn write_index_block(&mut self, block: &[u8]) -> Result<()> {
+        // Index blocks are minimally compressible so don't try
+        self.write_block(block, CompressionConfig::Uncompressed)
             .context("Failed to write index block")
     }
 
     #[tracing::instrument(level = "trace", skip_all)]
     fn write_small_value_block(&mut self, block: &[u8]) -> Result<()> {
-        self.write_block(block, None, false)
-            .context("Failed to write small value block")
+        self.write_block(
+            block,
+            CompressionConfig::TryCompress {
+                dict: None,
+                long_term: false,
+            },
+        )
+        .context("Failed to write small value block")
     }
 
     #[tracing::instrument(level = "trace", skip_all)]
     fn write_value_block(&mut self, block: &[u8]) -> Result<()> {
-        self.write_block(block, None, true)
-            .context("Failed to write value block")
+        self.write_block(
+            block,
+            CompressionConfig::TryCompress {
+                dict: None,
+                long_term: true,
+            },
+        )
+        .context("Failed to write value block")
     }
 
-    fn write_block(&mut self, block: &[u8], dict: Option<&[u8]>, long_term: bool) -> Result<()> {
-        let uncompressed_size = block.len().try_into().unwrap();
-        self.compress_block_into_buffer(block, dict, long_term)?;
-        let len = (self.buffer.len() + 4).try_into().unwrap();
+    fn write_block(&mut self, block: &[u8], compression: CompressionConfig<'_>) -> Result<()> {
+        let (uncompressed_size, data_to_write): (u32, &[u8]) = match compression {
+            CompressionConfig::TryCompress { dict, long_term } => {
+                self.compress_block_into_buffer(block, dict, long_term)?;
+                // Same threshold as LevelDB/RocksDB: require at least 12.5% savings to store
+                // compressed.
+                // See https://github.com/google/leveldb/blob/ac691084fdc5546421a55b25e7653d450e5a25fb/table/table_builder.cc#L164
+                // Uncompressed blocks take more time to read but we can directly leverage the mmap
+                // on the read side, compressed blocks need to be decompressed and managed in a
+                // cache. So we should only do it if we expect to save time.
+                if self.buffer.len() < block.len() - (block.len() / 8) {
+                    // Compression helped - use compressed data
+                    (block.len().try_into().unwrap(), self.buffer.as_slice())
+                } else {
+                    // Compression didn't help - use uncompressed with sentinel size value
+                    (0, block)
+                }
+            }
+            CompressionConfig::Uncompressed => (0, block),
+        };
+
+        let len: u32 = (data_to_write.len() + 4).try_into().unwrap();
         let offset = self
             .block_offsets
             .last()
@@ -292,10 +341,10 @@ impl<'l> BlockWriter<'l> {
 
         self.writer
             .write_u32::<BE>(uncompressed_size)
-            .context("Failed to write uncompressed size")?;
+            .context("Failed to write uncompressed_size")?;
         self.writer
-            .write_all(self.buffer)
-            .context("Failed to write compressed block")?;
+            .write_all(data_to_write)
+            .context("Failed to write block data")?;
         self.buffer.clear();
         Ok(())
     }
@@ -372,7 +421,7 @@ fn write_value_blocks(
                 value_locations.push((block_index, 0));
                 writer.write_value_block(value)?;
             }
-            EntryValue::MediumCompressed {
+            EntryValue::MediumRaw {
                 uncompressed_size,
                 block,
             } => {
@@ -436,7 +485,7 @@ fn write_key_blocks_and_compute_amqf(
                     value.len().try_into().unwrap(),
                 );
             }
-            EntryValue::Medium { .. } | EntryValue::MediumCompressed { .. } => {
+            EntryValue::Medium { .. } | EntryValue::MediumRaw { .. } => {
                 block.put_medium(entry, value_location.0);
             }
             EntryValue::Large { blob } => {
@@ -526,7 +575,7 @@ fn write_key_blocks_and_compute_amqf(
     }
     let _ = writer.next_block_index();
     index_block.finish();
-    writer.write_index_block(buffer, key_compression_dictionary)?;
+    writer.write_index_block(buffer)?;
     buffer.clear();
 
     Ok(turbo_bincode_encode(&AmqfBincodeWrapper(filter)).expect("AMQF serialization failed"))
diff --git a/turbopack/crates/turbo-tasks-backend/src/database/turbo/mod.rs b/turbopack/crates/turbo-tasks-backend/src/database/turbo/mod.rs
index ea1144fdd416c4..4b45d61b6f000c 100644
--- a/turbopack/crates/turbo-tasks-backend/src/database/turbo/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/database/turbo/mod.rs
@@ -9,7 +9,7 @@ use std::{
 use anyhow::{Ok, Result};
 use parking_lot::Mutex;
 use turbo_persistence::{
-    ArcSlice, CompactConfig, KeyBase, StoreKey, TurboPersistence, ValueBuffer,
+    ArcBytes, CompactConfig, KeyBase, StoreKey, TurboPersistence, ValueBuffer,
 };
 use turbo_tasks::{JoinHandle, message_queue::TimingEvent, spawn, turbo_tasks};
 
@@ -71,7 +71,7 @@ impl KeyValueDatabase for TurboKeyValueDatabase {
     }
 
     type ValueBuffer<'l>
-        = ArcSlice<u8>
+        = ArcBytes
     where
         Self: 'l;
 
@@ -176,7 +176,7 @@ pub struct TurboWriteBatch<'a> {
 
 impl<'a> BaseWriteBatch<'a> for TurboWriteBatch<'a> {
     type ValueBuffer<'l>
-        = ArcSlice<u8>
+        = ArcBytes
     where
         Self: 'l,
         'a: 'l;

PATCH

echo "Patch applied successfully."
