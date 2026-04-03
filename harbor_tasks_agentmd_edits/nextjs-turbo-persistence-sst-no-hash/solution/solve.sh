#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'BLOCK_TYPE_KEY_NO_HASH' turbopack/crates/turbo-persistence/src/static_sorted_file.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/README.md b/turbopack/crates/turbo-persistence/README.md
index 4ca9331dfefb1..e5ccef6bb6c74 100644
--- a/turbopack/crates/turbo-persistence/README.md
+++ b/turbopack/crates/turbo-persistence/README.md
@@ -85,7 +85,7 @@ The hashes are sorted.

 #### Key Block

-- 1 byte block type (1: key block)
+- 1 byte block type (1: key block with hash, 2: key block without hash)
 - 3 bytes entry count
 - foreach entry
   - 1 byte type
@@ -94,23 +94,30 @@ The hashes are sorted.

 A Key block contains n keys, which specify n key value pairs.

+The block type determines whether the key hash is stored per entry:
+
+- Block type 1 (with hash): Full 8-byte hash stored per entry
+- Block type 2 (no hash): No hash stored (for keys ≤ 32 bytes)
+
+During lookup, if block type is 2, the full hash is recomputed from the key data.
+
 Depending on the `type` field entry has a different format:

 - 0: normal key (small value)
-  - 8 bytes key hash
+  - 8 bytes key hash (if block type 1)
   - key data
   - 2 byte block index
   - 2 bytes size
   - 4 bytes position in block
 - 1: blob reference
-  - 8 bytes key hash
+  - 8 bytes key hash (if block type 1)
   - key data
   - 4 bytes sequence number
 - 2: deleted key / tombstone (no data)
-  - 8 bytes key hash
+  - 8 bytes key hash (if block type 1)
   - key data
 - 3: normal key (medium sized value)
-  - 8 bytes key hash
+  - 8 bytes key hash (if block type 1)
   - key data
   - 2 byte block index
 - 7: merge key (future)
@@ -119,14 +126,12 @@ Depending on the `type` field entry has a different format:
   - 3 bytes size
   - 4 bytes position in block
 - 8..255: inlined key (future)
-  - 8 bytes key hash
+  - 8 bytes key hash (if block type 1)
   - key data
   - type - 8 bytes value data

 The entries are sorted by key hash and key.

-TODO: 8 bytes key hash is a bit inefficient for small keys.
-
 #### Value Block

 - no header, all bytes are data referenced by other blocks
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
index 2233880f397d7..0767d85085870 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file.rs
@@ -21,8 +21,10 @@ use crate::{

 /// The block header for an index block.
 pub const BLOCK_TYPE_INDEX: u8 = 0;
-/// The block header for a key block.
-pub const BLOCK_TYPE_KEY: u8 = 1;
+/// The block header for a key block with 8-byte hash per entry.
+pub const BLOCK_TYPE_KEY_WITH_HASH: u8 = 1;
+/// The block header for a key block without hash.
+pub const BLOCK_TYPE_KEY_NO_HASH: u8 = 2;

 /// The tag for a small-sized value.
 pub const KEY_BLOCK_ENTRY_TYPE_SMALL: u8 = 0;
@@ -152,8 +154,15 @@ impl StaticSortedFile {
                 BLOCK_TYPE_INDEX => {
                     current_block = self.lookup_index_block(block, key_hash)?;
                 }
-                BLOCK_TYPE_KEY => {
-                    return self.lookup_key_block(block, key_hash, key, value_block_cache);
+                BLOCK_TYPE_KEY_WITH_HASH | BLOCK_TYPE_KEY_NO_HASH => {
+                    let has_hash = block_type == BLOCK_TYPE_KEY_WITH_HASH;
+                    return self.lookup_key_block(
+                        block,
+                        key_hash,
+                        key,
+                        has_hash,
+                        value_block_cache,
+                    );
                 }
                 _ => {
                     bail!("Invalid block type");
@@ -214,8 +223,10 @@ impl StaticSortedFile {
         mut block: &[u8],
         key_hash: u64,
         key: &K,
+        has_hash: bool,
         value_block_cache: &BlockCache,
     ) -> Result<SstLookupResult> {
+        let hash_len: u8 = if has_hash { 8 } else { 0 };
         let entry_count = block.read_u24::<BE>()? as usize;
         let offsets = &block[..entry_count * 4];
         let entries = &block[entry_count * 4..];
@@ -230,8 +241,11 @@ impl StaticSortedFile {
                 key: mid_key,
                 ty,
                 val: mid_val,
-            } = get_key_entry(offsets, entries, entry_count, m)?;
-            match key_hash.cmp(&mid_hash).then_with(|| key.cmp(mid_key)) {
+            } = get_key_entry(offsets, entries, entry_count, m, hash_len)?;
+
+            let comparison = compare_hash_key(mid_hash, mid_key, key_hash, key);
+
+            match comparison {
                 Ordering::Less => {
                     r = m;
                 }
@@ -429,6 +443,7 @@ struct CurrentKeyBlock {
     entries: ArcSlice<u8>,
     entry_count: usize,
     index: usize,
+    hash_len: u8,
 }

 struct CurrentIndexBlock {
@@ -461,7 +476,9 @@ impl<'l> StaticSortedFileIter<'l> {
                     index: 0,
                 });
             }
-            BLOCK_TYPE_KEY => {
+            BLOCK_TYPE_KEY_WITH_HASH | BLOCK_TYPE_KEY_NO_HASH => {
+                let has_hash = block_type == BLOCK_TYPE_KEY_WITH_HASH;
+                let hash_len = if has_hash { 8 } else { 0 };
                 let entry_count = block.read_u24::<BE>()? as usize;
                 let offsets_range = 4..4 + entry_count * 4;
                 let entries_range = 4 + entry_count * 4..block_arc.len();
@@ -472,6 +489,7 @@ impl<'l> StaticSortedFileIter<'l> {
                     entries,
                     entry_count,
                     index: 0,
+                    hash_len,
                 });
             }
             _ => {
@@ -489,10 +507,17 @@ impl<'l> StaticSortedFileIter<'l> {
                 entries,
                 entry_count,
                 index,
+                hash_len,
             }) = self.current_key_block.take()
             {
                 let GetKeyEntryResult { hash, key, ty, val } =
-                    get_key_entry(&offsets, &entries, entry_count, index)?;
+                    get_key_entry(&offsets, &entries, entry_count, index, hash_len)?;
+                // Convert hash slice to u64, computing from key if no hash stored
+                let full_hash = if hash.is_empty() {
+                    crate::key::hash_key(&key)
+                } else {
+                    u64::from_be_bytes(hash.try_into().unwrap())
+                };
                 let value = if ty == KEY_BLOCK_ENTRY_TYPE_MEDIUM {
                     let mut val = val;
                     let block = val.read_u16::<BE>()?;
@@ -508,7 +533,7 @@ impl<'l> StaticSortedFileIter<'l> {
                     LazyLookupValue::Eager(value)
                 };
                 let entry = LookupEntry {
-                    hash,
+                    hash: full_hash,
                     // Safety: The key is a valid slice of the entries.
                     key: unsafe { ArcSlice::new_unchecked(key, ArcSlice::full_arc(&entries)) },
                     value,
@@ -519,6 +544,7 @@ impl<'l> StaticSortedFileIter<'l> {
                         entries,
                         entry_count,
                         index: index + 1,
+                        hash_len,
                     });
                 }
                 return Ok(Some(entry));
@@ -546,19 +572,47 @@ impl<'l> StaticSortedFileIter<'l> {
 }

 struct GetKeyEntryResult<'l> {
-    hash: u64,
+    hash: &'l [u8],
     key: &'l [u8],
     ty: u8,
     val: &'l [u8],
 }

+/// Compares a query (full_hash + query_key) against an entry (entry_hash + entry_key).
+/// Returns the ordering of query relative to entry.
+/// When entry_hash is empty, computes full hash from entry_key.
+fn compare_hash_key<K: QueryKey>(
+    entry_hash: &[u8],
+    entry_key: &[u8],
+    full_hash: u64,
+    query_key: &K,
+) -> Ordering {
+    if entry_hash.is_empty() {
+        // No hash stored - compute full hash from entry key
+        let entry_full_hash = crate::key::hash_key(&entry_key);
+        match full_hash.cmp(&entry_full_hash) {
+            Ordering::Equal => query_key.cmp(entry_key),
+            ord => ord,
+        }
+    } else {
+        // Full 8-byte hash stored - compare hashes first
+        let full_hash_bytes = full_hash.to_be_bytes();
+        match full_hash_bytes[..].cmp(entry_hash) {
+            Ordering::Equal => query_key.cmp(entry_key),
+            ord => ord,
+        }
+    }
+}
+
 /// Reads a key entry from a key block.
 fn get_key_entry<'l>(
     offsets: &[u8],
     entries: &'l [u8],
     entry_count: usize,
     index: usize,
+    hash_len: u8,
 ) -> Result<GetKeyEntryResult<'l>> {
+    let hash_len_usize = hash_len as usize;
     let mut offset = &offsets[index * 4..];
     let ty = offset.read_u8()?;
     let start = offset.read_u24::<BE>()? as usize;
@@ -567,29 +621,30 @@ fn get_key_entry<'l>(
     } else {
         (&offsets[(index + 1) * 4 + 1..]).read_u24::<BE>()? as usize
     };
-    let hash = (&entries[start..start + 8]).read_u64::<BE>()?;
+    // Return the raw hash bytes slice (0-8 bytes depending on hash_len)
+    let hash = &entries[start..start + hash_len_usize];
     Ok(match ty {
         KEY_BLOCK_ENTRY_TYPE_SMALL => GetKeyEntryResult {
             hash,
-            key: &entries[start + 8..end - 8],
+            key: &entries[start + hash_len_usize..end - 8],
             ty,
             val: &entries[end - 8..end],
         },
         KEY_BLOCK_ENTRY_TYPE_MEDIUM => GetKeyEntryResult {
             hash,
-            key: &entries[start + 8..end - 2],
+            key: &entries[start + hash_len_usize..end - 2],
             ty,
             val: &entries[end - 2..end],
         },
         KEY_BLOCK_ENTRY_TYPE_BLOB => GetKeyEntryResult {
             hash,
-            key: &entries[start + 8..end - 4],
+            key: &entries[start + hash_len_usize..end - 4],
             ty,
             val: &entries[end - 4..end],
         },
         KEY_BLOCK_ENTRY_TYPE_DELETED => GetKeyEntryResult {
             hash,
-            key: &entries[start + 8..end],
+            key: &entries[start + hash_len_usize..end],
             ty,
             val: &[],
         },
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
index c105c8484c325..29ac7fa4e7dfd 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
@@ -14,8 +14,9 @@ use crate::{
     compression::compress_into_buffer,
     meta_file::{AmqfBincodeWrapper, MetaEntryFlags},
     static_sorted_file::{
-        BLOCK_TYPE_INDEX, BLOCK_TYPE_KEY, KEY_BLOCK_ENTRY_TYPE_BLOB, KEY_BLOCK_ENTRY_TYPE_DELETED,
-        KEY_BLOCK_ENTRY_TYPE_MEDIUM, KEY_BLOCK_ENTRY_TYPE_SMALL,
+        BLOCK_TYPE_INDEX, BLOCK_TYPE_KEY_NO_HASH, BLOCK_TYPE_KEY_WITH_HASH,
+        KEY_BLOCK_ENTRY_TYPE_BLOB, KEY_BLOCK_ENTRY_TYPE_DELETED, KEY_BLOCK_ENTRY_TYPE_MEDIUM,
+        KEY_BLOCK_ENTRY_TYPE_SMALL,
     },
 };

@@ -45,6 +46,11 @@ const COMPRESSION_DICTIONARY_SAMPLE_PER_ENTRY: usize = 100;
 /// The minimum bytes that are used per key entry for a sample.
 const MIN_COMPRESSION_DICTIONARY_SAMPLE_PER_ENTRY: usize = 16;

+/// Determines whether to store the hash per entry based on max key length.
+fn use_hash(max_key_len: usize) -> bool {
+    max_key_len > 32
+}
+
 /// Trait for entries from that SST files can be created
 pub trait Entry {
     /// Returns the hash of the key
@@ -431,9 +437,11 @@ fn write_key_blocks_and_compute_amqf(
     }
     let mut current_block_start = 0;
     let mut current_block_size = 0;
+    let mut current_block_max_key_len = 0;
     let mut last_hash = 0;
     for (i, entry) in entries.iter().enumerate() {
         let key_hash = entry.key_hash();
+        let key_len = entry.key_len();

         // Add to AMQF
         filter
@@ -443,13 +451,15 @@ fn write_key_blocks_and_compute_amqf(

         // Accumulate until the block is full
         if current_block_size > 0
-                && (current_block_size + entry.key_len() + KEY_BLOCK_ENTRY_META_OVERHEAD
+                && (current_block_size + key_len + KEY_BLOCK_ENTRY_META_OVERHEAD
                     > MAX_KEY_BLOCK_SIZE
                     || i - current_block_start >= MAX_KEY_BLOCK_ENTRIES) &&
                     // avoid breaking the block in the middle of a hash conflict
                     last_hash != key_hash
         {
-            let mut block = KeyBlockBuilder::new(buffer, (i - current_block_start) as u32);
+            let entry_count = i - current_block_start;
+            let has_hash = use_hash(current_block_max_key_len);
+            let mut block = KeyBlockBuilder::new(buffer, entry_count as u32, has_hash);
             for j in current_block_start..i {
                 let entry = &entries[j];
                 let value_location = &value_locations[j];
@@ -463,15 +473,19 @@ fn write_key_blocks_and_compute_amqf(
             writer.write_key_block(buffer, key_compression_dictionary)?;
             buffer.clear();
             current_block_size = 0;
+            current_block_max_key_len = 0;
             current_block_start = i;
         }
         current_block_size += entry.key_len() + KEY_BLOCK_ENTRY_META_OVERHEAD;
+        current_block_max_key_len = current_block_max_key_len.max(key_len);
         last_hash = key_hash;
     }

     // Finish the last block
     if current_block_size > 0 {
-        let mut block = KeyBlockBuilder::new(buffer, (entries.len() - current_block_start) as u32);
+        let entry_count = entries.len() - current_block_start;
+        let has_hash = use_hash(current_block_max_key_len);
+        let mut block = KeyBlockBuilder::new(buffer, entry_count as u32, has_hash);
         for j in current_block_start..entries.len() {
             let entry = &entries[j];
             let value_location = &value_locations[j];
@@ -510,20 +524,26 @@ fn write_key_blocks_and_compute_amqf(
 pub struct KeyBlockBuilder<'l> {
     current_entry: usize,
     header_size: usize,
+    has_hash: bool,
     buffer: &'l mut Vec<u8>,
 }

-/// The size of the key block header.
+/// The size of the key block header (block type + entry count).
 const KEY_BLOCK_HEADER_SIZE: usize = 4;

 impl<'l> KeyBlockBuilder<'l> {
     /// Creates a new key block builder for the number of entries.
-    pub fn new(buffer: &'l mut Vec<u8>, entry_count: u32) -> Self {
+    pub fn new(buffer: &'l mut Vec<u8>, entry_count: u32, has_hash: bool) -> Self {
         debug_assert!(entry_count < (1 << 24));

         const ESTIMATED_KEY_SIZE: usize = 16;
         buffer.reserve(entry_count as usize * ESTIMATED_KEY_SIZE);
-        buffer.write_u8(BLOCK_TYPE_KEY).unwrap();
+        let block_type = if has_hash {
+            BLOCK_TYPE_KEY_WITH_HASH
+        } else {
+            BLOCK_TYPE_KEY_NO_HASH
+        };
+        buffer.write_u8(block_type).unwrap();
         buffer.write_u24::<BE>(entry_count).unwrap();
         for _ in 0..entry_count {
             buffer.write_u32::<BE>(0).unwrap();
@@ -531,10 +551,19 @@ impl<'l> KeyBlockBuilder<'l> {
         Self {
             current_entry: 0,
             header_size: buffer.len(),
+            has_hash,
             buffer,
         }
     }

+    /// Writes the 8-byte hash if `has_hash` is true.
+    fn write_hash<E: Entry>(&mut self, entry: &E) {
+        if self.has_hash {
+            let hash_bytes = entry.key_hash().to_be_bytes();
+            self.buffer.extend_from_slice(&hash_bytes);
+        }
+    }
+
     /// Writes a small-sized value to the buffer.
     pub fn put_small<E: Entry>(
         &mut self,
@@ -548,7 +577,7 @@ impl<'l> KeyBlockBuilder<'l> {
         let header = (pos as u32) | ((KEY_BLOCK_ENTRY_TYPE_SMALL as u32) << 24);
         BE::write_u32(&mut self.buffer[header_offset..header_offset + 4], header);

-        self.buffer.write_u64::<BE>(entry.key_hash()).unwrap();
+        self.write_hash(entry);
         entry.write_key_to(self.buffer);
         self.buffer.write_u16::<BE>(value_block).unwrap();
         self.buffer.write_u16::<BE>(value_size).unwrap();
@@ -564,7 +593,7 @@ impl<'l> KeyBlockBuilder<'l> {
         let header = (pos as u32) | ((KEY_BLOCK_ENTRY_TYPE_MEDIUM as u32) << 24);
         BE::write_u32(&mut self.buffer[header_offset..header_offset + 4], header);

-        self.buffer.write_u64::<BE>(entry.key_hash()).unwrap();
+        self.write_hash(entry);
         entry.write_key_to(self.buffer);
         self.buffer.write_u16::<BE>(value_block).unwrap();

@@ -578,7 +607,7 @@ impl<'l> KeyBlockBuilder<'l> {
         let header = (pos as u32) | ((KEY_BLOCK_ENTRY_TYPE_DELETED as u32) << 24);
         BE::write_u32(&mut self.buffer[header_offset..header_offset + 4], header);

-        self.buffer.write_u64::<BE>(entry.key_hash()).unwrap();
+        self.write_hash(entry);
         entry.write_key_to(self.buffer);

         self.current_entry += 1;
@@ -591,7 +620,7 @@ impl<'l> KeyBlockBuilder<'l> {
         let header = (pos as u32) | ((KEY_BLOCK_ENTRY_TYPE_BLOB as u32) << 24);
         BE::write_u32(&mut self.buffer[header_offset..header_offset + 4], header);

-        self.buffer.write_u64::<BE>(entry.key_hash()).unwrap();
+        self.write_hash(entry);
         entry.write_key_to(self.buffer);
         self.buffer.write_u32::<BE>(blob).unwrap();

PATCH

echo "Patch applied successfully."
