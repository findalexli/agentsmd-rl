#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'MAX_INLINE_VALUE_SIZE' turbopack/crates/turbo-persistence/src/constants.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/README.md b/turbopack/crates/turbo-persistence/README.md
index e5ccef6bb6c745..d808205385159a 100644
--- a/turbopack/crates/turbo-persistence/README.md
+++ b/turbopack/crates/turbo-persistence/README.md
@@ -125,10 +125,10 @@ Depending on the `type` field entry has a different format:
   - 2 byte block index
   - 3 bytes size
   - 4 bytes position in block
-- 8..255: inlined key (future)
+- 8..255: inlined value (currently only values ≤8 bytes are inlined, though the format supports up to 247)
   - 8 bytes key hash (if block type 1)
   - key data
-  - type - 8 bytes value data
+  - (type - 8) bytes value data (inline, no separate value block)

 The entries are sorted by key hash and key.

diff --git a/turbopack/crates/turbo-persistence/src/arc_slice.rs b/turbopack/crates/turbo-persistence/src/arc_slice.rs
index 785331a9262fc5..721aab96da9309 100644
--- a/turbopack/crates/turbo-persistence/src/arc_slice.rs
+++ b/turbopack/crates/turbo-persistence/src/arc_slice.rs
@@ -2,6 +2,7 @@ use std::{
     borrow::Borrow,
     fmt::{self, Debug, Formatter},
     hash::{Hash, Hasher},
+    io::{self, Read},
     ops::{Deref, Range},
     sync::Arc,
 };
@@ -65,22 +66,18 @@ impl<T: Debug> Debug for ArcSlice<T> {

 impl<T: Eq> Eq for ArcSlice<T> {}

-impl<T> ArcSlice<T> {
-    /// Creates a new `ArcSlice` from a pointer to a slice and an `Arc`.
-    ///
-    /// # Safety
-    ///
-    /// The caller must ensure that the pointer is pointing to a valid slice that is kept alive by
-    /// the `Arc`.
-    pub unsafe fn new_unchecked(data: *const [T], arc: Arc<[T]>) -> Self {
-        Self { data, arc }
-    }
-
-    /// Get the backing arc
-    pub fn full_arc(this: &ArcSlice<T>) -> Arc<[T]> {
-        this.arc.clone()
+impl Read for ArcSlice<u8> {
+    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
+        let available = &**self;
+        let len = std::cmp::min(buf.len(), available.len());
+        buf[..len].copy_from_slice(&available[..len]);
+        // Advance the slice view
+        self.data = &available[len..] as *const [u8];
+        Ok(len)
     }
+}

+impl<T> ArcSlice<T> {
     /// Returns a new `ArcSlice` that points to a slice of the current slice.
     pub fn slice(self, range: Range<usize>) -> ArcSlice<T> {
         let data = &*self;
@@ -90,4 +87,17 @@ impl<T> ArcSlice<T> {
             arc: self.arc,
         }
     }
+
+    /// Creates a sub-slice from a slice reference that points into this ArcSlice's backing data.
+    ///
+    /// # Safety
+    ///
+    /// The caller must ensure that `subslice` points to memory within this ArcSlice's
+    /// backing Arc (not just within the current slice view, but anywhere in the original Arc).
+    pub unsafe fn slice_from_subslice(&self, subslice: &[T]) -> ArcSlice<T> {
+        Self {
+            data: subslice as *const [T],
+            arc: self.arc.clone(),
+        }
+    }
 }
diff --git a/turbopack/crates/turbo-persistence/src/collector_entry.rs b/turbopack/crates/turbo-persistence/src/collector_entry.rs
index 06dd0944524d18..633f5df8996075 100644
--- a/turbopack/crates/turbo-persistence/src/collector_entry.rs
+++ b/turbopack/crates/turbo-persistence/src/collector_entry.rs
@@ -1,6 +1,7 @@
 use std::cmp::Ordering;

 use crate::{
+    constants::MAX_INLINE_VALUE_SIZE,
     key::StoreKey,
     static_sorted_file_builder::{Entry, EntryValue},
 };
@@ -94,12 +95,21 @@ impl<K: StoreKey> Entry for CollectorEntry<K> {

     fn value(&self) -> EntryValue<'_> {
         match &self.value {
-            // Tiny values are stored the same way as Small in the SST file, they just have an
-            // optimized representation here
-            CollectorEntryValue::Tiny { value, len } => EntryValue::Small {
-                value: &value[..*len as usize],
-            },
-            CollectorEntryValue::Small { value } => EntryValue::Small { value },
+            CollectorEntryValue::Tiny { value, len } => {
+                let slice = &value[..*len as usize];
+                if slice.len() <= MAX_INLINE_VALUE_SIZE {
+                    EntryValue::Inline { value: slice }
+                } else {
+                    EntryValue::Small { value: slice }
+                }
+            }
+            CollectorEntryValue::Small { value } => {
+                if value.len() <= MAX_INLINE_VALUE_SIZE {
+                    EntryValue::Inline { value }
+                } else {
+                    EntryValue::Small { value }
+                }
+            }
             CollectorEntryValue::Medium { value } => EntryValue::Medium { value },
             CollectorEntryValue::Large { blob } => EntryValue::Large { blob: *blob },
             CollectorEntryValue::Deleted => EntryValue::Deleted,
diff --git a/turbopack/crates/turbo-persistence/src/constants.rs b/turbopack/crates/turbo-persistence/src/constants.rs
index 7fb697bdff6642..ae3b2dfc9d6974 100644
--- a/turbopack/crates/turbo-persistence/src/constants.rs
+++ b/turbopack/crates/turbo-persistence/src/constants.rs
@@ -5,6 +5,12 @@ pub const MAX_MEDIUM_VALUE_SIZE: usize = 64 * 1024 * 1024;
 // Note this must fit into 2 bytes length
 pub const MAX_SMALL_VALUE_SIZE: usize = 64 * 1024 - 1;

+/// Maximum size for inline values stored directly in key blocks.
+/// Currently 8 bytes (break-even with the 8-byte indirection overhead).
+/// Can be increased up to 247 bytes (type 255 - 8) if desired.
+/// See static_sorted_file.rs for the static assertion enforcing this limit.
+pub const MAX_INLINE_VALUE_SIZE: usize = 8;
+
 /// Maximum number of entries per SST file
 pub const MAX_ENTRIES_PER_INITIAL_FILE: usize = 256 * 1024;

diff --git a/turbopack/crates/turbo-persistence/src/lookup_entry.rs b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
index c55adca31eaeae..91b159de668ce9 100644
--- a/turbopack/crates/turbo-persistence/src/lookup_entry.rs
+++ b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
@@ -1,6 +1,6 @@
 use crate::{
     ArcSlice,
-    constants::MAX_SMALL_VALUE_SIZE,
+    constants::{MAX_INLINE_VALUE_SIZE, MAX_SMALL_VALUE_SIZE},
     static_sorted_file_builder::{Entry, EntryValue},
 };

@@ -9,6 +9,8 @@ pub enum LookupValue {
     /// The value was deleted.
     Deleted,
     /// The value is stored in the SST file.
+    ///
+    /// The ArcSlice will be pointing either at a keyblock or a value block in the SST
     Slice { value: ArcSlice<u8> },
     /// The value is stored in a blob file.
     Blob { sequence_number: u32 },
@@ -66,7 +68,9 @@ impl Entry for LookupEntry<'_> {
         match &self.value {
             LazyLookupValue::Eager(LookupValue::Deleted) => EntryValue::Deleted,
             LazyLookupValue::Eager(LookupValue::Slice { value }) => {
-                if value.len() > MAX_SMALL_VALUE_SIZE {
+                if value.len() <= MAX_INLINE_VALUE_SIZE {
+                    EntryValue::Inline { value }
+                } else if value.len() > MAX_SMALL_VALUE_SIZE {
                     EntryValue::Medium { value }
                 } else {
                     EntryValue::Small { value }
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
index 0767d85085870b..6d8533a551b99d 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
@@ -16,6 +16,7 @@ use crate::{
     QueryKey,
     arc_slice::ArcSlice,
     compression::decompress_into_arc,
+    constants::MAX_INLINE_VALUE_SIZE,
     lookup_entry::{LazyLookupValue, LookupEntry, LookupValue},
 };

@@ -34,6 +35,15 @@ pub const KEY_BLOCK_ENTRY_TYPE_BLOB: u8 = 1;
 pub const KEY_BLOCK_ENTRY_TYPE_DELETED: u8 = 2;
 /// The tag for a medium-sized value.
 pub const KEY_BLOCK_ENTRY_TYPE_MEDIUM: u8 = 3;
+/// The minimum tag for inline values. The actual size is (tag - INLINE_MIN).
+pub const KEY_BLOCK_ENTRY_TYPE_INLINE_MIN: u8 = 8;
+
+// Static assertion: MAX_INLINE_VALUE_SIZE must fit in the key type encoding.
+// Key types 8-255 encode inline values of size 0-247, so max is 255 - 8 = 247.
+const _: () = assert!(
+    MAX_INLINE_VALUE_SIZE <= (u8::MAX - KEY_BLOCK_ENTRY_TYPE_INLINE_MIN) as usize,
+    "MAX_INLINE_VALUE_SIZE exceeds what can be encoded in key type byte"
+);

 /// The result of a lookup operation.
 pub enum SstLookupResult {
@@ -147,17 +157,16 @@ impl StaticSortedFile {
     ) -> Result<SstLookupResult> {
         let mut current_block = self.meta.block_count - 1;
         loop {
-            let block = self.get_key_block(current_block, key_block_cache)?;
-            let mut block = &block[..];
-            let block_type = block.read_u8()?;
+            let mut key_block_arc = self.get_key_block(current_block, key_block_cache)?;
+            let block_type = key_block_arc.read_u8()?;
             match block_type {
                 BLOCK_TYPE_INDEX => {
-                    current_block = self.lookup_index_block(block, key_hash)?;
+                    current_block = self.lookup_index_block(&key_block_arc, key_hash)?;
                 }
                 BLOCK_TYPE_KEY_WITH_HASH | BLOCK_TYPE_KEY_NO_HASH => {
                     let has_hash = block_type == BLOCK_TYPE_KEY_WITH_HASH;
                     return self.lookup_key_block(
-                        block,
+                        key_block_arc,
                         key_hash,
                         key,
                         has_hash,
@@ -220,7 +229,7 @@ impl StaticSortedFile {
     /// Looks up a key in a key block and the value in a value block.
     fn lookup_key_block<K: QueryKey>(
         &self,
-        mut block: &[u8],
+        mut block: ArcSlice<u8>,
         key_hash: u64,
         key: &K,
         has_hash: bool,
@@ -251,7 +260,7 @@ impl StaticSortedFile {
                 }
                 Ordering::Equal => {
                     return Ok(self
-                        .handle_key_match(ty, mid_val, value_block_cache)?
+                        .handle_key_match(ty, mid_val, &block, value_block_cache)?
                         .into());
                 }
                 Ordering::Greater => {
@@ -267,6 +276,7 @@ impl StaticSortedFile {
         &self,
         ty: u8,
         mut val: &[u8],
+        key_block_arc: &ArcSlice<u8>,
         value_block_cache: &BlockCache,
     ) -> Result<LookupValue> {
         Ok(match ty {
@@ -290,7 +300,10 @@ impl StaticSortedFile {
             }
             KEY_BLOCK_ENTRY_TYPE_DELETED => LookupValue::Deleted,
             _ => {
-                bail!("Invalid key block entry type");
+                // Inline value — val is already the correct slice
+                // SAFETY: val points into key_block_arc's data
+                let value = unsafe { key_block_arc.slice_from_subslice(val) };
+                LookupValue::Slice { value }
             }
         })
     }
@@ -527,15 +540,15 @@ impl<'l> StaticSortedFileIter<'l> {
                         block,
                     }
                 } else {
-                    let value = self
-                        .this
-                        .handle_key_match(ty, val, self.value_block_cache)?;
+                    let value =
+                        self.this
+                            .handle_key_match(ty, val, &entries, self.value_block_cache)?;
                     LazyLookupValue::Eager(value)
                 };
                 let entry = LookupEntry {
                     hash: full_hash,
-                    // Safety: The key is a valid slice of the entries.
-                    key: unsafe { ArcSlice::new_unchecked(key, ArcSlice::full_arc(&entries)) },
+                    // SAFETY: key points into entries which is backed by the same Arc
+                    key: unsafe { entries.slice_from_subslice(key) },
                     value,
                 };
                 if index + 1 < entry_count {
@@ -604,6 +617,20 @@ fn compare_hash_key<K: QueryKey>(
     }
 }

+/// Returns the byte size of the value portion for a given key block entry type.
+fn entry_val_size(ty: u8) -> Result<usize> {
+    match ty {
+        KEY_BLOCK_ENTRY_TYPE_SMALL => Ok(8), // 2 bytes block index, 2 bytes size, 4 bytes position
+        KEY_BLOCK_ENTRY_TYPE_MEDIUM => Ok(2), // 2 bytes block index
+        KEY_BLOCK_ENTRY_TYPE_BLOB => Ok(4),  // 4 byte blob id
+        KEY_BLOCK_ENTRY_TYPE_DELETED => Ok(0), // no value
+        ty if ty >= KEY_BLOCK_ENTRY_TYPE_INLINE_MIN => {
+            Ok((ty - KEY_BLOCK_ENTRY_TYPE_INLINE_MIN) as usize)
+        }
+        _ => bail!("Invalid key block entry type"),
+    }
+}
+
 /// Reads a key entry from a key block.
 fn get_key_entry<'l>(
     offsets: &[u8],
@@ -623,33 +650,11 @@ fn get_key_entry<'l>(
     };
     // Return the raw hash bytes slice (0-8 bytes depending on hash_len)
     let hash = &entries[start..start + hash_len_usize];
-    Ok(match ty {
-        KEY_BLOCK_ENTRY_TYPE_SMALL => GetKeyEntryResult {
-            hash,
-            key: &entries[start + hash_len_usize..end - 8],
-            ty,
-            val: &entries[end - 8..end],
-        },
-        KEY_BLOCK_ENTRY_TYPE_MEDIUM => GetKeyEntryResult {
-            hash,
-            key: &entries[start + hash_len_usize..end - 2],
-            ty,
-            val: &entries[end - 2..end],
-        },
-        KEY_BLOCK_ENTRY_TYPE_BLOB => GetKeyEntryResult {
-            hash,
-            key: &entries[start + hash_len_usize..end - 4],
-            ty,
-            val: &entries[end - 4..end],
-        },
-        KEY_BLOCK_ENTRY_TYPE_DELETED => GetKeyEntryResult {
-            hash,
-            key: &entries[start + hash_len_usize..end],
-            ty,
-            val: &[],
-        },
-        _ => {
-            bail!("Invalid key block entry type");
-        }
+    let val_size = entry_val_size(ty)?;
+    Ok(GetKeyEntryResult {
+        hash,
+        key: &entries[start + hash_len_usize..end - val_size],
+        ty,
+        val: &entries[end - val_size..end],
     })
 }
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
index 29ac7fa4e7dfd4..b2042b47965d74 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
@@ -12,11 +12,12 @@ use turbo_bincode::{TurboBincodeBuffer, turbo_bincode_encode};

 use crate::{
     compression::compress_into_buffer,
+    constants::MAX_INLINE_VALUE_SIZE,
     meta_file::{AmqfBincodeWrapper, MetaEntryFlags},
     static_sorted_file::{
         BLOCK_TYPE_INDEX, BLOCK_TYPE_KEY_NO_HASH, BLOCK_TYPE_KEY_WITH_HASH,
-        KEY_BLOCK_ENTRY_TYPE_BLOB, KEY_BLOCK_ENTRY_TYPE_DELETED, KEY_BLOCK_ENTRY_TYPE_MEDIUM,
-        KEY_BLOCK_ENTRY_TYPE_SMALL,
+        KEY_BLOCK_ENTRY_TYPE_BLOB, KEY_BLOCK_ENTRY_TYPE_DELETED, KEY_BLOCK_ENTRY_TYPE_INLINE_MIN,
+        KEY_BLOCK_ENTRY_TYPE_MEDIUM, KEY_BLOCK_ENTRY_TYPE_SMALL,
     },
 };

@@ -67,6 +68,8 @@ pub trait Entry {
 /// Reference to a value
 #[derive(Copy, Clone)]
 pub enum EntryValue<'l> {
+    /// Inline value stored directly in the key block.
+    Inline { value: &'l [u8] },
     /// Small-sized value. They are stored in shared value blocks.
     Small { value: &'l [u8] },
     /// Medium-sized value. They are stored in their own value block.
@@ -372,7 +375,8 @@ fn write_value_blocks(
                 value_locations.push((block_index, 0));
                 writer.write_compressed_block(uncompressed_size, block)?;
             }
-            EntryValue::Deleted | EntryValue::Large { .. } => {
+            EntryValue::Inline { .. } | EntryValue::Deleted | EntryValue::Large { .. } => {
+                // Inline values are stored in the key block, not in value blocks
                 value_locations.push((0, 0));
             }
         }
@@ -416,6 +420,9 @@ fn write_key_blocks_and_compute_amqf(
         block: &mut KeyBlockBuilder,
     ) {
         match entry.value() {
+            EntryValue::Inline { value } => {
+                block.put_inline(entry, value);
+            }
             EntryValue::Small { value } => {
                 block.put_small(
                     entry,
@@ -627,6 +634,22 @@ impl<'l> KeyBlockBuilder<'l> {
         self.current_entry += 1;
     }

+    /// Writes an inline value directly to the key block.
+    pub fn put_inline<E: Entry>(&mut self, entry: &E, value: &[u8]) {
+        debug_assert!(value.len() <= MAX_INLINE_VALUE_SIZE);
+        let pos = self.buffer.len() - self.header_size;
+        let header_offset = KEY_BLOCK_HEADER_SIZE + self.current_entry * 4;
+        let entry_type = KEY_BLOCK_ENTRY_TYPE_INLINE_MIN + value.len() as u8;
+        let header = (pos as u32) | ((entry_type as u32) << 24);
+        BE::write_u32(&mut self.buffer[header_offset..header_offset + 4], header);
+
+        self.write_hash(entry);
+        entry.write_key_to(self.buffer);
+        self.buffer.extend_from_slice(value);
+
+        self.current_entry += 1;
+    }
+
     /// Returns the key block buffer
     pub fn finish(self) -> &'l mut Vec<u8> {
         self.buffer

PATCH

echo "Patch applied successfully."
