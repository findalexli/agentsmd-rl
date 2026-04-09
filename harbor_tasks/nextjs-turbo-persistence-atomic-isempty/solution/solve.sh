#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'is_empty: AtomicBool,' turbopack/crates/turbo-persistence/src/db.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/src/db.rs b/turbopack/crates/turbo-persistence/src/db.rs
index 0957abe259140f..f2a098ff3868e6 100644
--- a/turbopack/crates/turbo-persistence/src/db.rs
+++ b/turbopack/crates/turbo-persistence/src/db.rs
@@ -117,6 +117,9 @@ pub struct TurboPersistence<S: ParallelScheduler, const FAMILIES: usize> {
     read_only: bool,
     /// The inner state of the database. Writing will update that.
     inner: RwLock<Inner<FAMILIES>>,
+    /// A flag to indicate if the database is empty (no meta files). This is an atomic mirror of
+    /// `inner.meta_files.is_empty()` to avoid taking a lock on the hot path.
+    is_empty: AtomicBool,
     /// A flag to indicate if a write operation is currently active. Prevents multiple concurrent
     /// write operations.
     active_write_operation: AtomicBool,
@@ -191,6 +194,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
                 accessed_key_hashes: [(); FAMILIES]
                     .map(|_| DashSet::with_hasher(BuildNoHashHasher::default())),
             }),
+            is_empty: AtomicBool::new(true),
             active_write_operation: AtomicBool::new(false),
             key_block_cache: BlockCache::with(
                 KEY_BLOCK_CACHE_SIZE as usize / KEY_BLOCK_AVG_SIZE,
@@ -395,6 +399,8 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
         }

         let inner = self.inner.get_mut();
+        self.is_empty
+            .store(meta_files.is_empty(), Ordering::Relaxed);
         inner.meta_files = meta_files;
         inner.current_sequence_number = current;
         Ok(true)
@@ -442,7 +448,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>

     /// Returns true if the database is empty.
     pub fn is_empty(&self) -> bool {
-        self.inner.read().meta_files.is_empty()
+        self.is_empty.load(Ordering::Relaxed)
     }

     /// Starts a new WriteBatch for the database. Only a single write operation is allowed at a
@@ -686,6 +692,8 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
                 }
             });
             inner.meta_files.reverse();
+            self.is_empty
+                .store(inner.meta_files.is_empty(), Ordering::Relaxed);
             has_delete_file = !sst_seq_numbers_to_delete.is_empty()
                 || !blob_seq_numbers_to_delete.is_empty()
                 || !meta_seq_numbers_to_delete.is_empty();

PATCH

echo "Patch applied successfully."
