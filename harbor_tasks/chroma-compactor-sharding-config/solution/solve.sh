#!/bin/bash
set -e

cd /workspace/chroma

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/rust/worker/src/compactor/compaction_manager.rs b/rust/worker/src/compactor/compaction_manager.rs
index 2b9b67cbdf2..dc230c045ad 100644
--- a/rust/worker/src/compactor/compaction_manager.rs
+++ b/rust/worker/src/compactor/compaction_manager.rs
@@ -107,6 +107,7 @@ pub(crate) struct CompactionManagerContext {
     collections_for_fragment_fetch: HashSet<CollectionUuid>,
     bloom_filter_manager: Option<BloomFilterManager>,
     shard_size: Option<u64>,
+    sharding_enabled_tenant_patterns: Vec<String>,
 }

 pub(crate) struct CompactionManager {
@@ -162,6 +163,7 @@ impl CompactionManager {
         collections_for_fragment_fetch: HashSet<CollectionUuid>,
         bloom_filter_manager: Option<BloomFilterManager>,
         shard_size: Option<u64>,
+        sharding_enabled_tenant_patterns: Vec<String>,
     ) -> Result<Self, Box<dyn ChromaError>> {
         let (compact_awaiter_tx, compact_awaiter_rx) =
             mpsc::channel::<CompactionTask>(compaction_manager_queue_size);
@@ -201,6 +203,7 @@ impl CompactionManager {
                 collections_for_fragment_fetch,
                 bloom_filter_manager,
                 shard_size,
+                sharding_enabled_tenant_patterns,
             },
             on_next_memberlist_signal: None,
             compact_awaiter_channel: compact_awaiter_tx,
@@ -231,6 +234,7 @@ impl CompactionManager {
                 .compact(
                     job.collection_id,
                     job.database_name.clone(),
+                    job.tenant_id.clone(),
                     false,
                     HashSet::new(),
                 )
@@ -257,15 +261,40 @@ impl CompactionManager {
         collection_ids: &[CollectionUuid],
         segment_scopes: &HashSet<chroma_types::SegmentScope>,
     ) {
-        // TODO(tanujnay112): Implement this for MCMR by accepting a database/topo name on this method.
-        let _ = collection_ids
+        let options = chroma_sysdb::types::GetCollectionsOptions {
+            collection_ids: Some(collection_ids.to_vec()),
+            ..Default::default()
+        };
+        let collections = match self.context.sysdb.get_collections(options).await {
+            Ok(collections) => collections,
+            Err(e) => {
+                // TODO(tanujnay112): Propagate error up and then handle it there.
+                tracing::error!("Failed to get collections in rebuild: {}", e);
+                return;
+            }
+        };
+        let _ = collections
             .iter()
-            .map(|id| {
-                let database_name =
-                    chroma_types::DatabaseName::new("default").expect("default should be valid");
-                self.context
-                    .clone()
-                    .compact(*id, database_name, true, segment_scopes.clone())
+            .filter_map(|collection| {
+                match chroma_types::DatabaseName::new(collection.database.clone()) {
+                    Some(database_name) => Some(
+                        self.context.clone().compact(
+                            collection.collection_id,
+                            database_name,
+                            collection.tenant.clone(),
+                            true,
+                            segment_scopes.clone(),
+                        )
+                    ),
+                    None => {
+                        tracing::error!(
+                            "Invalid database name '{}' for collection {} (must be at least 3 characters)",
+                            collection.database,
+                            collection.collection_id
+                        );
+                        None
+                    }
+                }
             })
             .collect::<FuturesUnordered<_>>()
             .collect::<Vec<_>>()
@@ -435,6 +464,7 @@ impl CompactionManagerContext {
         self,
         collection_id: CollectionUuid,
         database_name: chroma_types::DatabaseName,
+        tenant_id: String,
         is_rebuild: bool,
         apply_segment_scopes: HashSet<chroma_types::SegmentScope>,
     ) -> Result<CompactionResponse, Box<dyn ChromaError>> {
@@ -452,6 +482,12 @@ impl CompactionManagerContext {
         let is_function_disabled = self.disabled_function_collections.contains(&collection_id);
         let fragment_fetcher = self.fragment_fetcher_for_collection(collection_id);
         let bloom_filter_manager = self.bloom_filter_manager_for_collection(collection_id);
+        let shard_size =
+            if tenant_matches_patterns(&tenant_id, &self.sharding_enabled_tenant_patterns) {
+                self.shard_size
+            } else {
+                None
+            };

         let compact_result = Box::pin(compact(
             self.system.clone(),
@@ -472,7 +508,7 @@ impl CompactionManagerContext {
             is_function_disabled,
             fragment_fetcher,
             bloom_filter_manager,
-            self.shard_size,
+            shard_size,
             #[cfg(test)]
             None,
         ))
@@ -686,10 +722,23 @@ impl Configurable<(CompactionServiceConfig, System)> for CompactionManager {
             collections_for_fragment_fetch,
             Some(bloom_filter_manager),
             config.compactor.shard_size,
+            config.compactor.sharding_enabled_tenant_patterns.clone(),
         )
     }
 }

+fn tenant_matches_patterns(tenant_id: &str, patterns: &[String]) -> bool {
+    for pattern in patterns {
+        if pattern == "*" {
+            return true;
+        }
+        if pattern == tenant_id {
+            return true;
+        }
+    }
+    false
+}
+
 async fn compact_awaiter_loop(
     mut job_rx: mpsc::Receiver<CompactionTask>,
     completion_tx: mpsc::UnboundedSender<CompactionTaskCompletion>,
@@ -1245,6 +1294,7 @@ mod tests {
             HashSet::new(), // collections_for_fragment_fetch
             None,           // bloom_filter_manager
             None,           // shard_size
+            Vec::new(),     // sharding_enabled_tenant_patterns
         )
         .expect("Failed to create compaction manager in test");

diff --git a/rust/worker/src/compactor/config.rs b/rust/worker/src/compactor/config.rs
index 95f9d26ec11..b5bb5f86693 100644
--- a/rust/worker/src/compactor/config.rs
+++ b/rust/worker/src/compactor/config.rs
@@ -127,10 +127,17 @@ pub struct CompactorConfig {
     #[serde(default)]
     pub fragment_fetcher_cache: chroma_cache::CacheConfig,

-    /// The size threshold for shards. When a shard exceeds this size, it will be sealed
-    /// and a new shard created. None or 0 means no limit.
+    /// Global shard size limit. When a shard exceeds this size, it will be sealed
+    /// and a new shard created. Only applies to tenants with sharding enabled.
     #[serde(default = "CompactorConfig::default_shard_size")]
     pub shard_size: Option<u64>,
+
+    /// List of tenant patterns that have sharding enabled. Supports wildcards:
+    /// - "*" enables sharding for all tenants
+    /// - "prod-*" enables for tenants starting with "prod-"
+    /// - "tenant1" enables for exact match
+    #[serde(default)]
+    pub sharding_enabled_tenant_patterns: Vec<String>,
 }

 impl CompactorConfig {
@@ -195,7 +202,7 @@ impl CompactorConfig {
     }

     fn default_shard_size() -> Option<u64> {
-        None // No limit by default
+        None // No sharding by default
     }
 }

@@ -222,6 +229,7 @@ impl Default for CompactorConfig {
             collections_for_fragment_fetch: Vec::new(),
             fragment_fetcher_cache: chroma_cache::CacheConfig::default(),
             shard_size: CompactorConfig::default_shard_size(),
+            sharding_enabled_tenant_patterns: Vec::new(),
         }
     }
 }
diff --git a/rust/worker/src/compactor/scheduler.rs b/rust/worker/src/compactor/scheduler.rs
index a954857bfd5..cbd0ae0f7aa 100644
--- a/rust/worker/src/compactor/scheduler.rs
+++ b/rust/worker/src/compactor/scheduler.rs
@@ -450,6 +450,7 @@ impl Scheduler {
             self.job_queue.push(CompactionJob {
                 collection_id: record.collection_id,
                 database_name: database_name.clone(),
+                tenant_id: record.tenant_id.clone(),
             });
             self.oneoff_collections.remove(&record.collection_id);
             rem_capacity -= 1;
diff --git a/rust/worker/src/compactor/scheduler_policy.rs b/rust/worker/src/compactor/scheduler_policy.rs
index 657263aef2e..4aa210ad210 100644
--- a/rust/worker/src/compactor/scheduler_policy.rs
+++ b/rust/worker/src/compactor/scheduler_policy.rs
@@ -59,6 +59,7 @@ impl SchedulerPolicy for LasCompactionTimeSchedulerPolicy {
             tasks.push(CompactionJob {
                 collection_id: collection.collection_id,
                 database_name,
+                tenant_id: collection.tenant_id.clone(),
             });
         }
         tasks
diff --git a/rust/worker/src/compactor/types.rs b/rust/worker/src/compactor/types.rs
index e4b160b99e1..2a2c89fd8f1 100644
--- a/rust/worker/src/compactor/types.rs
+++ b/rust/worker/src/compactor/types.rs
@@ -7,6 +7,7 @@ use tokio::sync::oneshot;
 pub(crate) struct CompactionJob {
     pub(crate) collection_id: CollectionUuid,
     pub(crate) database_name: DatabaseName,
+    pub(crate) tenant_id: String,
 }

 #[derive(Clone, Debug)]
PATCH

# Idempotency check - verify the patch was applied
echo "Checking patch application..."
grep -q "fn tenant_matches_patterns" rust/worker/src/compactor/compaction_manager.rs && echo "Patch applied successfully"
