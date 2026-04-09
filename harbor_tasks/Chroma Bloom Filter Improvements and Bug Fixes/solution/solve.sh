#!/bin/bash
set -e

cd /workspace/chroma

# Check if already patched (idempotency)
if grep -q "Create an independent copy that does not share" rust/segment/src/bloom_filter.rs; then
    echo "Already patched, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/rust/segment/src/blockfile_record.rs b/rust/segment/src/blockfile_record.rs
index 4fcfb703c07..0b24b0857f5 100644
--- a/rust/segment/src/blockfile_record.rs
+++ b/rust/segment/src/blockfile_record.rs
@@ -662,8 +662,8 @@ impl RecordSegmentWriter {

         let serialized_bloom_filter = match (self.bloom_filter.take(), &self.bloom_filter_manager) {
             (Some(bf), Some(manager)) => {
-                Some(manager.commit(bf, &self.prefix_path).await.map_err(|_| {
-                    Box::new(ApplyMaterializedLogError::BloomFilterSerializationError)
+                Some(manager.commit(bf, &self.prefix_path).await.map_err(|e| {
+                    Box::new(ApplyMaterializedLogError::BloomFilterSerializationError(e))
                         as Box<dyn ChromaError>
                 })?)
             }
@@ -706,8 +706,8 @@ pub enum ApplyMaterializedLogError {
     Materialization(#[from] LogMaterializerError),
     #[error("Error applying materialized records to spann segment: {0}")]
     SpannSegmentError(#[from] SpannSegmentWriterError),
-    #[error("Bloom filter serialization failed during commit")]
-    BloomFilterSerializationError,
+    #[error("Bloom filter serialization failed during commit: {0}")]
+    BloomFilterSerializationError(BloomFilterError),
     #[cfg(feature = "usearch")]
     #[error(transparent)]
     QuantizedSpannSegmentError(#[from] crate::quantized_spann::QuantizedSpannSegmentError),
@@ -725,7 +725,7 @@ impl ChromaError for ApplyMaterializedLogError {
             ApplyMaterializedLogError::HnswIndex(_) => ErrorCodes::Internal,
             ApplyMaterializedLogError::Materialization(e) => e.code(),
             ApplyMaterializedLogError::SpannSegmentError(e) => e.code(),
-            ApplyMaterializedLogError::BloomFilterSerializationError => ErrorCodes::Internal,
+            ApplyMaterializedLogError::BloomFilterSerializationError(e) => e.code(),
             #[cfg(feature = "usearch")]
             ApplyMaterializedLogError::QuantizedSpannSegmentError(e) => e.code(),
         }
@@ -822,19 +822,14 @@ impl RecordSegmentFlusher {
             }
         }

-        // Write serialized bloom filter to its pre-determined storage path.
-        // Failures are non-fatal — the bloom filter will be rebuilt on the next compaction cycle.
         if let Some(serialized_bloom_filter) = &self.serialized_bloom_filter {
             let bloom_filter_path = serialized_bloom_filter.path().to_string();
-            match serialized_bloom_filter.save().await {
-                Ok(()) => {
-                    tracing::info!(path = %bloom_filter_path, "Persisted bloom filter to storage");
-                    flushed_files.insert(USER_ID_BLOOM_FILTER.to_string(), vec![bloom_filter_path]);
-                }
-                Err(e) => {
-                    tracing::warn!(error = ?e, "Failed to persist bloom filter, skipping");
-                }
-            }
+            serialized_bloom_filter
+                .save()
+                .await
+                .map_err(|e| Box::new(e) as Box<dyn ChromaError>)?;
+            tracing::info!(path = %bloom_filter_path, "Persisted bloom filter to storage");
+            flushed_files.insert(USER_ID_BLOOM_FILTER.to_string(), vec![bloom_filter_path]);
         }

         Ok(flushed_files)
@@ -1020,7 +1015,9 @@ impl RecordSegmentReader<'_> {

     /// Lazily loads the bloom filter using the two-tier heuristic.
     /// Called internally when a plan requests bloom filter usage.
-    async fn ensure_bloom_filter(&self) {
+    /// Fetch the bloom filter from storage (via the manager cache) and populate
+    /// the local `OnceCell`. Only call when a storage fetch is acceptable.
+    async fn fetch_bloom_filter(&self) {
         self.bloom_filter
             .get_or_init(|| async {
                 let (manager, path) = match (&self.bloom_filter_manager, &self.bloom_filter_path) {
@@ -1032,17 +1029,35 @@ impl RecordSegmentReader<'_> {
             .await;
     }

+    /// Try to populate the local `OnceCell` from the manager's in-memory cache
+    /// without triggering a storage fetch. Returns quickly if already loaded or
+    /// if the bloom filter isn't cached.
+    async fn try_load_bloom_filter_from_cache(&self) {
+        if self.bloom_filter.get().is_some() {
+            return;
+        }
+        let (manager, path) = match (&self.bloom_filter_manager, &self.bloom_filter_path) {
+            (Some(mgr), Some(p)) => (mgr, p.as_str()),
+            _ => return,
+        };
+        if let Some(bf) = manager.get_if_cached(path).await {
+            let _ = self.bloom_filter.set(Some(bf));
+        }
+    }
+
     pub async fn get_offset_id_for_user_id(
         &self,
         user_id: &str,
         plan: &RecordSegmentReaderOptions,
     ) -> Result<Option<u32>, Box<dyn ChromaError>> {
         if plan.use_bloom_filter {
-            self.ensure_bloom_filter().await;
-            if let Some(Some(bf)) = self.bloom_filter.get() {
-                if !bf.contains(user_id) {
-                    return Ok(None);
-                }
+            self.fetch_bloom_filter().await;
+        } else {
+            self.try_load_bloom_filter_from_cache().await;
+        }
+        if let Some(Some(bf)) = self.bloom_filter.get() {
+            if !bf.contains(user_id) {
+                return Ok(None);
             }
         }
         self.user_id_to_id.get("", user_id).await
@@ -1141,7 +1156,9 @@ impl RecordSegmentReader<'_> {
     ) {
         // Lazy load the bloom filter if it is needed.
         if plan.use_bloom_filter {
-            self.ensure_bloom_filter().await;
+            self.fetch_bloom_filter().await;
+        } else {
+            self.try_load_bloom_filter_from_cache().await;
         }

         let filtered: Vec<&str> = if let Some(Some(bf)) = self.bloom_filter.get() {
diff --git a/rust/segment/src/bloom_filter.rs b/rust/segment/src/bloom_filter.rs
index 3afc80a9c7f..5cdeac40a17 100644
--- a/rust/segment/src/bloom_filter.rs
+++ b/rust/segment/src/bloom_filter.rs
@@ -97,6 +97,24 @@ impl<T: Hash + ?Sized> Clone for BloomFilter<T> {
     }
 }

+impl<T: Hash + ?Sized> BloomFilter<T> {
+    /// Create an independent copy that does not share the underlying
+    /// `Arc<BloomFilterInner>`. Mutations on the returned copy (inserts,
+    /// deletes, counter bumps) will not affect the original, and vice versa.
+    pub fn deep_clone(&self) -> Self {
+        Self {
+            inner: Arc::new(BloomFilterInner {
+                filter: self.inner.filter.clone(),
+                live_count: AtomicU64::new(self.inner.live_count.load(Ordering::Relaxed)),
+                stale_count: AtomicU64::new(self.inner.stale_count.load(Ordering::Relaxed)),
+                capacity: self.inner.capacity,
+            }),
+            id: self.id,
+            _phantom: PhantomData,
+        }
+    }
+}
+
 impl<T: Hash + ?Sized> std::fmt::Debug for BloomFilter<T> {
     fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
         f.debug_struct("BloomFilter")
@@ -136,7 +154,7 @@ impl ChromaError for BloomFilterError {
 }

 impl<T: Hash + ?Sized> BloomFilter<T> {
-    /// Create a new bloom filter sized for `expected_items` with a 0.001% false positive rate.
+    /// Create a new bloom filter sized for `expected_items` with a 0.1% false positive rate.
     pub fn new(expected_items: u64) -> Self {
         let capacity = expected_items.max(1);
         let filter = AtomicBloomFilter::with_false_pos(DEFAULT_FALSE_POSITIVE_RATE)
@@ -244,8 +262,8 @@ impl<T: Hash + ?Sized> BloomFilter<T> {
             id: self.id,
             bits,
             num_hashes: self.inner.filter.num_hashes(),
-            live_count: self.inner.live_count.load(Ordering::SeqCst),
-            stale_count: self.inner.stale_count.load(Ordering::SeqCst),
+            live_count: self.inner.live_count.load(Ordering::Relaxed),
+            stale_count: self.inner.stale_count.load(Ordering::Relaxed),
             capacity: self.inner.capacity,
         };
         let bytes = bincode::serialize(&repr)
@@ -269,8 +287,8 @@ impl<T: Hash + ?Sized> BloomFilter<T> {
             id: self.id,
             bits,
             num_hashes: inner.filter.num_hashes(),
-            live_count: inner.live_count.load(Ordering::SeqCst),
-            stale_count: inner.stale_count.load(Ordering::SeqCst),
+            live_count: inner.live_count.load(Ordering::Relaxed),
+            stale_count: inner.stale_count.load(Ordering::Relaxed),
             capacity: inner.capacity,
         };
         bincode::serialize(&repr).map_err(|e| BloomFilterError::Serialization(e.to_string()))
@@ -424,6 +442,11 @@ impl BloomFilterManager {
         }
     }

+    /// Extract the cache key (UUID portion) from a full storage path.
+    fn cache_key_from_path(path: &str) -> String {
+        path.rsplit('/').next().unwrap_or(path).to_string()
+    }
+
     /// Cache the bloom filter and return the serialized form ready for flush.
     /// The full storage path is constructed from `prefix_path` and the filter's id.
     pub async fn commit(
@@ -432,19 +455,19 @@ impl BloomFilterManager {
         prefix_path: &str,
     ) -> Result<BloomFilterFlusher, BloomFilterError> {
         let path = Self::format_key(prefix_path, bf.id());
-        let key = bf.id().to_string();
-        self.inner.cache.insert(key, bf.clone()).await;
+        let key = Self::cache_key_from_path(&path);
+        self.inner.cache.insert(key, bf.deep_clone()).await;
         bf.into_bytes(self.inner.storage.clone(), path)
     }

     /// Look up a bloom filter by its storage path. Returns from cache if present,
     /// otherwise loads from storage, caches it, and returns it.
     pub async fn get(&self, path: &str) -> Result<BloomFilter<str>, BloomFilterError> {
-        // The path ends with the bloom filter's UUID; use it as cache key.
-        let cache_key = path.rsplit('/').next().unwrap_or(path).to_string();
+        let cache_key = Self::cache_key_from_path(path);
         if let Ok(Some(cached)) = self.inner.cache.get(&cache_key).await {
             return Ok(cached);
         }
+        let inner = self.inner.clone();
         let (bf, _) = self
             .inner
             .storage
@@ -453,25 +476,25 @@ impl BloomFilterManager {
                 GetOptions::new(StorageRequestPriority::P0).with_parallelism(),
                 move |bytes_result| async move {
                     let bytes = bytes_result?;
-                    BloomFilter::<str>::from_bytes(&bytes).map_err(|e| StorageError::Message {
-                        message: e.to_string(),
-                    })
+                    let bf = BloomFilter::<str>::from_bytes(&bytes).map_err(|e| {
+                        StorageError::Message {
+                            message: e.to_string(),
+                        }
+                    })?;
+                    inner.cache.insert(cache_key, bf.deep_clone()).await;
+                    Ok(bf)
                 },
             )
             .await
             .map_err(BloomFilterError::Storage)?;
-        // TODO(Sanket-temp): Should deep copy bloom filter here to avoid modifying the original one.
-        self.inner
-            .cache
-            .insert(bf.id().to_string(), bf.clone())
-            .await;
         Ok(bf)
     }

     /// Returns the bloom filter only if it's already in the cache.
     /// Does NOT fetch from storage. Near-zero cost.
     pub async fn get_if_cached(&self, path: &str) -> Option<BloomFilter<str>> {
-        self.inner.cache.get(&path.to_string()).await.ok().flatten()
+        let cache_key = Self::cache_key_from_path(path);
+        self.inner.cache.get(&cache_key).await.ok().flatten()
     }

     pub fn storage_fetch_threshold(&self) -> usize {
@@ -751,4 +774,46 @@ mod tests {
         assert!(!mgr.is_enabled_for_collection(c2));
         assert!(!mgr.is_enabled_for_collection(c3));
     }
+
+    #[test]
+    fn test_deep_clone_isolation() {
+        let original = BloomFilter::<str>::new(1000);
+        original.insert("a");
+        original.insert("b");
+
+        let cloned = original.deep_clone();
+
+        // Both start with the same state.
+        assert_eq!(original.live_count(), 2);
+        assert_eq!(cloned.live_count(), 2);
+        assert!(cloned.contains("a"));
+        assert!(cloned.contains("b"));
+
+        // Mutate the original — clone should be unaffected.
+        original.insert("c");
+        original.mark_deleted();
+        assert_eq!(original.live_count(), 2);
+        assert_eq!(original.stale_count(), 1);
+        assert!(original.contains("c"));
+        assert_eq!(cloned.live_count(), 2);
+        assert_eq!(cloned.stale_count(), 0);
+
+        // Mutate the clone — original should be unaffected.
+        cloned.insert("d");
+        assert!(cloned.contains("d"));
+        assert_eq!(cloned.live_count(), 3);
+        assert_eq!(original.live_count(), 2);
+
+        // Filter bits are independent: "c" was inserted into original only,
+        // "d" was inserted into clone only.
+        assert!(!cloned.contains("c"));
+        assert!(!original.contains("d"));
+
+        // A regular clone() is shallow — shares the same inner Arc.
+        let shallow = original.clone();
+        assert!(std::sync::Arc::ptr_eq(&original.inner, &shallow.inner));
+        shallow.insert("e");
+        assert!(original.contains("e"), "shallow clone shares filter bits");
+        assert_eq!(original.live_count(), 3, "shallow clone shares counters");
+    }
 }
PATCH

echo "Patch applied successfully."
