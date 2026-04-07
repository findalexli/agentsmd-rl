#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'MIN_SMALL_VALUE_BLOCK_SIZE' turbopack/crates/turbo-persistence/src/constants.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/README.md b/turbopack/crates/turbo-persistence/README.md
index d808205385159..8af39c9bba727 100644
--- a/turbopack/crates/turbo-persistence/README.md
+++ b/turbopack/crates/turbo-persistence/README.md
@@ -23,14 +23,29 @@ There are four different file types:
 - Delete files (`*.del`): These files contain a list of sequence numbers of files that should be considered as deleted.
 - Meta files (`*.meta`): These files contain metadata about the SST files. They contains the hash range and a AMQF for quick filtering.

-Therefore there are there value types:
+Therefore there are these value types:

-- INLINE: Small values that are stored directly in the `*.sst` files.
-- BLOB: Large values that are stored in `*.blob` files.
+- INLINE: Values ≤ 8 bytes stored directly in key blocks within `*.sst` files.
+- SMALL: Values 9–4096 bytes packed into shared value blocks within `*.sst` files.
+- MEDIUM: Values 4097 bytes – 64 MB stored in dedicated value blocks within `*.sst` files.
+- BLOB: Values > 64 MB stored in separate `*.blob` files.
 - DELETED: Values that are deleted. (Tombstone)
 - Future:
   - MERGE: An application specific update operation that is applied on the old value.

+### Value type trade-offs
+
+|                       | Inline            | Small                                           | Medium                                | Blob                                      |
+| --------------------- | ----------------- | ----------------------------------------------- | ------------------------------------- | ----------------------------------------- |
+| Size                  | ≤ 8 B             | 9 B .. 4 kB                                     | 4 kB .. 64 MB                         | > 64 MB                                   |
+| Compression unit      | key block         | shared value block (≥ 8 kB)                     | dedicated value block                 | separate file                             |
+| Compression unit size | ≤ 16 kB           | 8 kB .. 12 kB                                   | 4 kB .. 64 MB                         | > 64 MB                                   |
+| Access cost           | no extra overhead | decompress shared block (~8 kB)                 | decompress value size                 | open separate file, decompress value size |
+| Storage overhead      | 0                 | 8 B in key block + 8 B per ~8 kB in block table | 2 B in key block + 8 B in block table | 4 B in key block + 4 B in blob header     |
+| Compaction            | re-compressed     | re-compressed                                   | copied compressed                     | pointer copied                            |
+
+Small value blocks are emitted once they accumulate at least `MIN_SMALL_VALUE_BLOCK_SIZE` (8 kB) of data. This means actual block sizes range from 8 kB up to 8 kB + `MAX_SMALL_VALUE_SIZE` (4 kB) = 12 kB. This provides a good balance between compression efficiency (blocks ≥ 4 kB don't need a compression dictionary) and access cost (only ~8–12 kB needs to be decompressed per lookup).
+
 ### Meta file

 A meta file can contain metadata about multiple SST files. The metadata is stored in a single file to avoid having too many small files.
diff --git a/turbopack/crates/turbo-persistence/src/collector.rs b/turbopack/crates/turbo-persistence/src/collector.rs
index 4cd0c83ad53ad..1408fd35a0e57 100644
--- a/turbopack/crates/turbo-persistence/src/collector.rs
+++ b/turbopack/crates/turbo-persistence/src/collector.rs
@@ -7,6 +7,7 @@ use crate::{
         DATA_THRESHOLD_PER_INITIAL_FILE, MAX_ENTRIES_PER_INITIAL_FILE, MAX_SMALL_VALUE_SIZE,
     },
     key::{StoreKey, hash_key},
+    value_block_count_tracker::ValueBlockCountTracker,
 };

 /// A collector accumulates entries that should be eventually written to a file. It keeps track of
@@ -14,6 +15,7 @@ use crate::{
 pub struct Collector<K: StoreKey, const SIZE_SHIFT: usize = 0> {
     total_key_size: usize,
     total_value_size: usize,
+    value_block_tracker: ValueBlockCountTracker,
     entries: Vec<CollectorEntry<K>>,
 }

@@ -23,6 +25,7 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
         Self {
             total_key_size: 0,
             total_value_size: 0,
+            value_block_tracker: ValueBlockCountTracker::new(),
             entries: Vec::with_capacity(MAX_ENTRIES_PER_INITIAL_FILE >> SIZE_SHIFT),
         }
     }
@@ -37,6 +40,7 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
         self.entries.len() >= MAX_ENTRIES_PER_INITIAL_FILE >> SIZE_SHIFT
             || self.total_key_size + self.total_value_size
                 > DATA_THRESHOLD_PER_INITIAL_FILE >> SIZE_SHIFT
+            || self.value_block_tracker.is_full()
     }

     /// Adds a normal key-value pair to the collector.
@@ -64,6 +68,8 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
         };
         self.total_key_size += key.len();
         self.total_value_size += value.len();
+        self.value_block_tracker
+            .track(value.is_medium_value(), value.small_value_size());
         self.entries.push(CollectorEntry { key, value });
     }

@@ -97,6 +103,10 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
     pub fn add_entry(&mut self, entry: CollectorEntry<K>) {
         self.total_key_size += entry.key.len();
         self.total_value_size += entry.value.len();
+        self.value_block_tracker.track(
+            entry.value.is_medium_value(),
+            entry.value.small_value_size(),
+        );
         self.entries.push(entry);
     }

@@ -112,6 +122,7 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
         self.entries.clear();
         self.total_key_size = 0;
         self.total_value_size = 0;
+        self.value_block_tracker.reset();
     }

     /// Drains all entries from the collector in un-sorted order. This can be used to move the
@@ -119,6 +130,7 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
     pub fn drain(&mut self) -> impl Iterator<Item = CollectorEntry<K>> + '_ {
         self.total_key_size = 0;
         self.total_value_size = 0;
+        self.value_block_tracker.reset();
         self.entries.drain(..)
     }

@@ -127,5 +139,6 @@ impl<K: StoreKey, const SIZE_SHIFT: usize> Collector<K, SIZE_SHIFT> {
         drop(take(&mut self.entries));
         self.total_key_size = 0;
         self.total_value_size = 0;
+        self.value_block_tracker.reset();
     }
 }
diff --git a/turbopack/crates/turbo-persistence/src/collector_entry.rs b/turbopack/crates/turbo-persistence/src/collector_entry.rs
index 633f5df899607..a5ca345d058f8 100644
--- a/turbopack/crates/turbo-persistence/src/collector_entry.rs
+++ b/turbopack/crates/turbo-persistence/src/collector_entry.rs
@@ -45,6 +45,22 @@ impl CollectorEntryValue {
             CollectorEntryValue::Deleted => 0,
         }
     }
+
+    /// Returns true if this value gets its own dedicated value block.
+    pub fn is_medium_value(&self) -> bool {
+        matches!(self, CollectorEntryValue::Medium { .. })
+    }
+
+    /// Returns the value size if it will be packed into a small value block, or 0 otherwise.
+    pub fn small_value_size(&self) -> usize {
+        match self {
+            CollectorEntryValue::Tiny { len, .. } if (*len as usize) > MAX_INLINE_VALUE_SIZE => {
+                *len as usize
+            }
+            CollectorEntryValue::Small { value } => value.len(),
+            _ => 0,
+        }
+    }
 }

 pub struct EntryKey<K: StoreKey> {
diff --git a/turbopack/crates/turbo-persistence/src/constants.rs b/turbopack/crates/turbo-persistence/src/constants.rs
index 6d53866f2ca91..d3132d34cae88 100644
--- a/turbopack/crates/turbo-persistence/src/constants.rs
+++ b/turbopack/crates/turbo-persistence/src/constants.rs
@@ -3,7 +3,11 @@ pub const MAX_MEDIUM_VALUE_SIZE: usize = 64 * 1024 * 1024;

 /// Values larger than this become separate value blocks
 // Note this must fit into 2 bytes length
-pub const MAX_SMALL_VALUE_SIZE: usize = 64 * 1024 - 1;
+// Note that a medium value has 14 bytes of extra overhead compared to a small value.
+// Note that we want to benefit from better compression by merging small values together, so we can
+// avoid a compression dictionary. At ≥4kB block size, compression works well without a dictionary.
+// Note that medium values can be copied without decompression during compaction.
+pub const MAX_SMALL_VALUE_SIZE: usize = 4096;

 /// Maximum size for inline values stored directly in key blocks.
 /// Currently 8 bytes (break-even with the 8-byte indirection overhead).
@@ -27,6 +31,17 @@ pub const DATA_THRESHOLD_PER_COMPACTED_FILE: usize = 256 * 1024 * 1024;
 /// MAX_ENTRIES_PER_INITIAL_FILE and DATA_THRESHOLD_PER_INITIAL_FILE.
 pub const THREAD_LOCAL_SIZE_SHIFT: usize = 7;

+/// The minimum bytes that should accumulate before emitting a small value block.
+/// Blocks are emitted once they reach this size, so actual block sizes range from
+/// MIN_SMALL_VALUE_BLOCK_SIZE to MIN_SMALL_VALUE_BLOCK_SIZE + MAX_SMALL_VALUE_SIZE.
+pub const MIN_SMALL_VALUE_BLOCK_SIZE: usize = 8 * 1024;
+
+/// Maximum number of value blocks per SST file.
+/// Must leave room for key blocks + index block within u16::MAX total blocks.
+/// Uses u16::MAX / 2 to account for the 50/50 merge-and-split at end of compaction,
+/// which can double the block count before splitting.
+pub const MAX_VALUE_BLOCK_COUNT: usize = u16::MAX as usize / 2;
+
 /// Maximum RAM bytes for key block cache
 pub const KEY_BLOCK_CACHE_SIZE: u64 = 400 * 1024 * 1024;
 pub const KEY_BLOCK_AVG_SIZE: usize = 16 * 1024;
diff --git a/turbopack/crates/turbo-persistence/src/db.rs b/turbopack/crates/turbo-persistence/src/db.rs
index 2aa8bafebc603..a677f6a6b9f24 100644
--- a/turbopack/crates/turbo-persistence/src/db.rs
+++ b/turbopack/crates/turbo-persistence/src/db.rs
@@ -37,6 +37,7 @@ use crate::{
     sst_filter::SstFilter,
     static_sorted_file::{BlockCache, SstLookupResult},
     static_sorted_file_builder::{StaticSortedFileBuilderMeta, write_static_stored_file},
+    value_block_count_tracker::ValueBlockCountTracker,
     write_batch::{FinishResult, WriteBatch},
 };

@@ -1051,6 +1052,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
                                     entries: Vec<LookupEntry<'l>>,
                                     total_key_size: usize,
                                     total_value_size: usize,
+                                    value_block_tracker: ValueBlockCountTracker,
                                     last_entries: Vec<LookupEntry<'l>>,
                                     last_entries_total_key_size: usize,
                                     new_sst_files:
@@ -1076,13 +1078,19 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
                                             let key_size = current.key.len();
                                             let value_size =
                                                 current.value.uncompressed_size_in_sst();
+                                            let is_medium = current.value.is_medium_value();
+                                            let small_size = current.value.small_value_size();
                                             collector.total_key_size += key_size;
                                             collector.total_value_size += value_size;
+                                            collector
+                                                .value_block_tracker
+                                                .track(is_medium, small_size);

                                             if collector.total_key_size + collector.total_value_size
                                                 > DATA_THRESHOLD_PER_COMPACTED_FILE
                                                 || collector.entries.len()
                                                     >= MAX_ENTRIES_PER_COMPACTED_FILE
+                                                || collector.value_block_tracker.is_full()
                                             {
                                                 let selected_total_key_size =
                                                     collector.last_entries_total_key_size;
@@ -1094,6 +1102,9 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
                                                     collector.total_key_size - key_size;
                                                 collector.total_key_size = key_size;
                                                 collector.total_value_size = value_size;
+                                                collector
+                                                    .value_block_tracker
+                                                    .reset_to(is_medium, small_size);

                                                 if !collector.entries.is_empty() {
                                                     let seq = sequence_number
diff --git a/turbopack/crates/turbo-persistence/src/lib.rs b/turbopack/crates/turbo-persistence/src/lib.rs
index 5d5eef8fcf28c..588c484c94585 100644
--- a/turbopack/crates/turbo-persistence/src/lib.rs
+++ b/turbopack/crates/turbo-persistence/src/lib.rs
@@ -19,6 +19,7 @@ mod parallel_scheduler;
 mod sst_filter;
 mod static_sorted_file;
 mod static_sorted_file_builder;
+mod value_block_count_tracker;
 mod value_buf;
 mod write_batch;

diff --git a/turbopack/crates/turbo-persistence/src/lookup_entry.rs b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
index 91b159de668ce..da1c5fa7ebb11 100644
--- a/turbopack/crates/turbo-persistence/src/lookup_entry.rs
+++ b/turbopack/crates/turbo-persistence/src/lookup_entry.rs
@@ -39,6 +39,31 @@ impl LazyLookupValue<'_> {
             } => *uncompressed_size as usize,
         }
     }
+
+    /// Returns true if this value gets its own dedicated value block.
+    pub fn is_medium_value(&self) -> bool {
+        match self {
+            LazyLookupValue::Eager(LookupValue::Slice { value })
+                if value.len() > MAX_SMALL_VALUE_SIZE =>
+            {
+                true
+            }
+            LazyLookupValue::Medium { .. } => true,
+            _ => false,
+        }
+    }
+
+    /// Returns the value size if it will be packed into a small value block, or 0 otherwise.
+    pub fn small_value_size(&self) -> usize {
+        match self {
+            LazyLookupValue::Eager(LookupValue::Slice { value })
+                if value.len() > MAX_INLINE_VALUE_SIZE && value.len() <= MAX_SMALL_VALUE_SIZE =>
+            {
+                value.len()
+            }
+            _ => 0,
+        }
+    }
 }

 /// An entry from a SST file lookup.
diff --git a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
index b2042b47965d7..3be860dfd307f 100644
--- a/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
+++ b/turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs
@@ -12,7 +12,7 @@ use turbo_bincode::{TurboBincodeBuffer, turbo_bincode_encode};

 use crate::{
     compression::compress_into_buffer,
-    constants::MAX_INLINE_VALUE_SIZE,
+    constants::{MAX_INLINE_VALUE_SIZE, MIN_SMALL_VALUE_BLOCK_SIZE},
     meta_file::{AmqfBincodeWrapper, MetaEntryFlags},
     static_sorted_file::{
         BLOCK_TYPE_INDEX, BLOCK_TYPE_KEY_NO_HASH, BLOCK_TYPE_KEY_WITH_HASH,
@@ -26,12 +26,17 @@ const MAX_KEY_BLOCK_ENTRIES: usize = MAX_KEY_BLOCK_SIZE / KEY_BLOCK_ENTRY_META_O
 /// The maximum bytes that should go into a single key block
 // Note this must fit into 3 bytes length
 const MAX_KEY_BLOCK_SIZE: usize = 16 * 1024;
-/// Overhead of bytes that should be counted for entries in a key block in addition to the key size
-const KEY_BLOCK_ENTRY_META_OVERHEAD: usize = 8;
+/// Overhead of bytes that should be counted for entries in a key block in addition to the key size.
+/// This covers the worst case (small values):
+/// - 1 byte type (key block header)
+/// - 3 bytes position (key block header)
+/// - 8 bytes hash (optional, but unknown at collection time)
+/// - 2 bytes block index
+/// - 2 bytes size
+/// - 4 bytes position in block
+const KEY_BLOCK_ENTRY_META_OVERHEAD: usize = 20;
 /// The maximum number of entries that should go into a single small value block
-const MAX_SMALL_VALUE_BLOCK_ENTRIES: usize = MAX_SMALL_VALUE_BLOCK_SIZE;
-/// The maximum bytes that should go into a single small value block
-const MAX_SMALL_VALUE_BLOCK_SIZE: usize = 64 * 1024;
+const MAX_SMALL_VALUE_BLOCK_ENTRIES: usize = MIN_SMALL_VALUE_BLOCK_SIZE;
 /// The aimed false positive rate for the AMQF
 const AMQF_FALSE_POSITIVE_RATE: f64 = 0.01;

@@ -341,12 +346,15 @@ fn write_value_blocks(
     for (i, entry) in entries.iter().enumerate() {
         match entry.value() {
             EntryValue::Small { value } => {
-                if current_block_size + value.len() > MAX_SMALL_VALUE_BLOCK_SIZE
-                    || current_block_count + 1 >= MAX_SMALL_VALUE_BLOCK_ENTRIES
+                value_locations.push((0, current_block_size.try_into().unwrap()));
+                current_block_size += value.len();
+                current_block_count += 1;
+                if current_block_size >= MIN_SMALL_VALUE_BLOCK_SIZE
+                    || current_block_count >= MAX_SMALL_VALUE_BLOCK_ENTRIES
                 {
                     let block_index = writer.next_block_index();
                     buffer.reserve(current_block_size);
-                    for j in current_block_start..i {
+                    for j in current_block_start..=i {
                         if let EntryValue::Small { value } = &entries[j].value() {
                             buffer.extend_from_slice(value);
                             value_locations[j].0 = block_index;
@@ -354,13 +362,10 @@ fn write_value_blocks(
                     }
                     writer.write_small_value_block(buffer)?;
                     buffer.clear();
-                    current_block_start = i;
+                    current_block_start = i + 1;
                     current_block_size = 0;
                     current_block_count = 0;
                 }
-                value_locations.push((0, current_block_size.try_into().unwrap()));
-                current_block_size += value.len();
-                current_block_count += 1;
             }
             EntryValue::Medium { value } => {
                 let block_index = writer.next_block_index();
diff --git a/turbopack/crates/turbo-persistence/src/value_block_count_tracker.rs b/turbopack/crates/turbo-persistence/src/value_block_count_tracker.rs
new file mode 100644
index 00000000000000..95cde74b182ef1
--- /dev/null
+++ b/turbopack/crates/turbo-persistence/src/value_block_count_tracker.rs
@@ -0,0 +1,47 @@
+use crate::constants::{MAX_VALUE_BLOCK_COUNT, MIN_SMALL_VALUE_BLOCK_SIZE};
+
+/// Tracks the number of value blocks that will be created for a set of entries.
+/// Used to prevent exceeding the u16 block index limit in SST files.
+#[derive(Default)]
+pub struct ValueBlockCountTracker {
+    value_block_count: usize,
+    current_small_value_block_size: usize,
+}
+
+impl ValueBlockCountTracker {
+    pub fn new() -> Self {
+        Self::default()
+    }
+
+    /// Track a new entry's value. Call with `is_medium=true` for medium values
+    /// (1 dedicated block each), or `small_value_size > 0` for small block values.
+    pub fn track(&mut self, is_medium: bool, small_value_size: usize) {
+        if is_medium {
+            self.value_block_count += 1;
+        } else if small_value_size > 0 {
+            self.current_small_value_block_size += small_value_size;
+            if self.current_small_value_block_size >= MIN_SMALL_VALUE_BLOCK_SIZE {
+                self.value_block_count += 1;
+                self.current_small_value_block_size = 0;
+            }
+        }
+    }
+
+    /// Returns true if the tracked value block count has reached the maximum.
+    pub fn is_full(&self) -> bool {
+        self.value_block_count + (self.current_small_value_block_size > 0) as usize
+            >= MAX_VALUE_BLOCK_COUNT
+    }
+
+    /// Reset the tracker to empty.
+    pub fn reset(&mut self) {
+        self.value_block_count = 0;
+        self.current_small_value_block_size = 0;
+    }
+
+    /// Reset the tracker to contain only the given entry.
+    pub fn reset_to(&mut self, is_medium: bool, small_value_size: usize) {
+        self.value_block_count = if is_medium { 1 } else { 0 };
+        self.current_small_value_block_size = small_value_size;
+    }
+}

PATCH

echo "Patch applied successfully."
