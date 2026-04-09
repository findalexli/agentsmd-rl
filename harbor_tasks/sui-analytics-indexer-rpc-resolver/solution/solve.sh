#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch from PR #26041
patch -p1 <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index d268f3748038..707afdd4eed3 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -14300,7 +14300,6 @@ dependencies = [
  "futures",
  "gcp-bigquery-client",
  "indexmap 2.8.0",
- "lru 0.10.1",
  "move-binary-format",
  "move-bytecode-utils",
  "move-core-types",
@@ -14327,6 +14326,7 @@ dependencies = [
  "sui-package-resolver",
  "sui-rpc",
  "sui-rpc-api",
+ "sui-rpc-resolver",
  "sui-storage",
  "sui-types",
  "tap",
@@ -14336,7 +14336,6 @@ dependencies = [
  "tokio",
  "tokio-util 0.7.18",
  "tracing",
- "typed-store",
  "url",
  "zstd 0.12.3+zstd.1.5.2",
 ]
diff --git a/crates/sui-analytics-indexer/Cargo.toml b/crates/sui-analytics-indexer/Cargo.toml
index 2ad16fc5aa12..a2a0938a75e2 100644
--- a/crates/sui-analytics-indexer/Cargo.toml
+++ b/crates/sui-analytics-indexer/Cargo.toml
@@ -35,12 +35,11 @@ arrow-array.workspace = true
 fastcrypto = { workspace = true, features = ["copy_key"] }
 sui-analytics-indexer-derive.workspace = true
 eyre.workspace = true
-tempfile.workspace = true
 sui-types.workspace = true
 telemetry-subscribers.workspace = true
 sui-rpc-api.workspace = true
 sui-storage.workspace = true
-typed-store.workspace = true
+sui-rpc-resolver.workspace = true
 move-binary-format.workspace = true
 move-bytecode-utils.workspace = true
 sui-json-rpc-types.workspace = true
@@ -50,7 +49,6 @@ gcp-bigquery-client = "0.27.0"
 snowflake-api.workspace = true
 tap.workspace = true
 serde_yaml.workspace = true
-lru.workspace = true
 scoped-futures.workspace = true
 sui-futures.workspace = true
 sui-indexer-alt-framework.workspace = true
diff --git a/crates/sui-analytics-indexer/src/handlers/mod.rs b/crates/sui-analytics-indexer/src/handlers/mod.rs
index 5760205dcddc..8fdc1744f029 100644
--- a/crates/sui-analytics-indexer/src/handlers/mod.rs
+++ b/crates/sui-analytics-indexer/src/handlers/mod.rs
@@ -10,6 +10,7 @@
 use crate::metrics::Metrics;

 pub mod handler;
+pub mod system_package_eviction;
 pub mod tables;

 pub use handler::AnalyticsHandler;
diff --git a/crates/sui-analytics-indexer/src/handlers/system_package_eviction.rs b/crates/sui-analytics-indexer/src/handlers/system_package_eviction.rs
new file mode 100644
index 000000000000..fcc73131005d
--- /dev/null
+++ b/crates/sui-analytics-indexer/src/handlers/system_package_eviction.rs
@@ -0,0 +1,62 @@
+// Copyright (c) Mysten Labs, Inc.
+// SPDX-License-Identifier: Apache-2.0
+
+use std::sync::Arc;
+use std::sync::atomic::{AtomicU64, Ordering};
+
+use anyhow::Result;
+use async_trait::async_trait;
+use sui_indexer_alt_framework::pipeline::Processor;
+use sui_indexer_alt_framework::pipeline::sequential;
+use sui_indexer_alt_framework::store::Store;
+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+use sui_types::SYSTEM_PACKAGE_ADDRESSES;
+use sui_types::full_checkpoint_content::Checkpoint;
+
+use crate::store::AnalyticsStore;
+
+pub struct SystemPackageEviction {
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+    last_epoch: AtomicU64,
+}
+
+impl SystemPackageEviction {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
+        Self {
+            package_cache,
+            last_epoch: AtomicU64::new(u64::MAX),
+        }
+    }
+}
+
+#[async_trait]
+impl Processor for SystemPackageEviction {
+    const NAME: &'static str = "SystemPackageEviction";
+    type Value = ();
+
+    async fn process(&self, checkpoint: &Arc<Checkpoint>) -> Result<Vec<()>> {
+        let epoch = checkpoint.summary.data().epoch;
+        if self.last_epoch.swap(epoch, Ordering::Relaxed) != epoch {
+            self.package_cache
+                .evict(SYSTEM_PACKAGE_ADDRESSES.iter().copied());
+        }
+        Ok(vec![])
+    }
+}
+
+#[async_trait]
+impl sequential::Handler for SystemPackageEviction {
+    type Store = AnalyticsStore;
+    type Batch = ();
+
+    fn batch(&self, _batch: &mut (), _values: std::vec::IntoIter<()>) {}
+
+    async fn commit<'a>(
+        &self,
+        _batch: &(),
+        _conn: &mut <AnalyticsStore as Store>::Connection<'a>,
+    ) -> Result<usize> {
+        Ok(0)
+    }
+}
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/df.rs b/crates/sui-analytics-indexer/src/handlers/tables/df.rs
index 90bf7d7bf014..f7b1f2463afc 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/df.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/df.rs
@@ -24,17 +24,20 @@ use sui_types::object::bounded_visitor::BoundedVisitor;
 use tap::tap::TapFallible;
 use tracing::warn;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::DynamicFieldRow;

 pub struct DynamicFieldProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl DynamicFieldProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -56,9 +59,7 @@ impl DynamicFieldProcessor {
             return Ok(None);
         }

-        let layout = self
-            .package_cache
-            .resolver_for_epoch(epoch)
+        let layout = Resolver::new(self.package_cache.clone())
             .type_layout(move_object.type_().clone().into())
             .await?;
         let object_id = object.id();
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/event.rs b/crates/sui-analytics-indexer/src/handlers/tables/event.rs
index 9fbb4c98ac2e..547811179a86 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/event.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/event.rs
@@ -13,17 +13,20 @@ use sui_types::effects::TransactionEffectsAPI;
 use sui_types::event::Event;
 use sui_types::full_checkpoint_content::Checkpoint;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::EventRow;

 pub struct EventProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl EventProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -63,9 +66,7 @@ impl Processor for EventProcessor {
                         contents,
                     } = event;

-                    let layout = self
-                        .package_cache
-                        .resolver_for_epoch(epoch)
+                    let layout = Resolver::new(self.package_cache.clone())
                         .type_layout(move_core_types::language_storage::TypeTag::Struct(
                             Box::new(type_.clone()),
                         ))
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/object.rs b/crates/sui-analytics-indexer/src/handlers/tables/object.rs
index 8608e56294e5..b15012c9c2f6 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/object.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/object.rs
@@ -13,6 +13,12 @@ use sui_types::base_types::ObjectID;
 use sui_types::full_checkpoint_content::Checkpoint;
 use sui_types::object::Object;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_package_resolver::error::Error as ResolverError;
+use sui_rpc_api::Client;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
 use crate::handlers::tables::ObjectStatusTracker;
 use crate::handlers::tables::get_is_consensus;
@@ -21,25 +27,27 @@ use crate::handlers::tables::get_owner_address;
 use crate::handlers::tables::get_owner_type;
 use crate::handlers::tables::initial_shared_version;
 use crate::metrics::Metrics;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::ObjectRow;
 use crate::tables::ObjectStatus;

 pub struct ObjectProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+    rpc_client: Client,
     package_filter: Option<ObjectID>,
     metrics: Metrics,
 }

 impl ObjectProcessor {
     pub fn new(
-        package_cache: Arc<PackageCache>,
+        package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+        rpc_url: &str,
         package_filter: &Option<String>,
         metrics: Metrics,
     ) -> Self {
         Self {
             package_cache,
+            rpc_client: Client::new(rpc_url).expect("invalid rpc url"),
             package_filter: package_filter
                 .clone()
                 .map(|x| ObjectID::from_hex_literal(&x).unwrap()),
@@ -47,6 +55,22 @@ impl ObjectProcessor {
         }
     }

+    async fn get_original_package_id(
+        &self,
+        id: move_core_types::account_address::AccountAddress,
+    ) -> anyhow::Result<ObjectID> {
+        let object = self
+            .rpc_client
+            .clone()
+            .get_object(ObjectID::from(id))
+            .await
+            .map_err(|_| ResolverError::PackageNotFound(id))?;
+        let sui_types::object::Data::Package(p) = &object.data else {
+            return Err(ResolverError::NotAPackage(id).into());
+        };
+        Ok(p.original_package_id())
+    }
+
     async fn check_type_hierarchy(
         &self,
         type_tag: &TypeTag,
@@ -71,11 +95,21 @@ impl ObjectProcessor {
         }

         // Resolve original package IDs in parallel
-        let mut original_ids = JoinSet::new();
+        let mut original_ids: JoinSet<anyhow::Result<ObjectID>> = JoinSet::new();

         for id in package_ids {
-            let package_cache = self.package_cache.clone();
-            original_ids.spawn(async move { package_cache.get_original_package_id(id).await });
+            let client = self.rpc_client.clone();
+            original_ids.spawn(async move {
+                let object = client
+                    .clone()
+                    .get_object(ObjectID::from(id))
+                    .await
+                    .map_err(|_| ResolverError::PackageNotFound(id))?;
+                let sui_types::object::Data::Package(p) = &object.data else {
+                    anyhow::bail!("not a package: {id}");
+                };
+                Ok(p.original_package_id())
+            });
         }

         // Check if any resolved ID matches our target
@@ -104,12 +138,7 @@ impl ObjectProcessor {
             .struct_tag()
             .and_then(|tag| object.data.try_as_move().map(|mo| (tag, mo.contents())))
         {
-            match get_move_struct(
-                &tag,
-                contents,
-                &self.package_cache.resolver_for_epoch(epoch),
-            )
-            .await
+            match get_move_struct(&tag, contents, &Resolver::new(self.package_cache.clone())).await
             {
                 Ok(move_struct) => Some(move_struct),
                 Err(err)
@@ -150,10 +179,7 @@ impl ObjectProcessor {

         let is_match = if let Some(package_id) = self.package_filter {
             if let Some(object_type) = object_type {
-                let original_package_id = self
-                    .package_cache
-                    .get_original_package_id(package_id.into())
-                    .await?;
+                let original_package_id = self.get_original_package_id(package_id.into()).await?;

                 let type_tag: TypeTag = object_type.clone().into();
                 self.check_type_hierarchy(&type_tag, original_package_id)
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs b/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
index dd58c7f23878..e0cf24afec3a 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
@@ -10,19 +10,22 @@ use sui_indexer_alt_framework::pipeline::Processor;
 use sui_types::base_types::EpochId;
 use sui_types::full_checkpoint_content::Checkpoint;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
 use crate::handlers::tables::get_move_struct;
 use crate::handlers::tables::parse_struct;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::WrappedObjectRow;

 pub struct WrappedObjectProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl WrappedObjectProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -58,7 +61,7 @@ impl Processor for WrappedObjectProcessor {
                     match get_move_struct(
                         &tag,
                         contents,
-                        &self.package_cache.resolver_for_epoch(epoch),
+                        &Resolver::new(self.package_cache.clone()),
                     )
                     .await
                     {
diff --git a/crates/sui-analytics-indexer/src/indexer.rs b/crates/sui-analytics-indexer/src/indexer.rs
index ef7684be2855..13504beba095 100644
--- a/crates/sui-analytics-indexer/src/indexer.rs
+++ b/crates/sui-analytics-indexer/src/indexer.rs
@@ -26,10 +26,12 @@ use sui_indexer_alt_framework::pipeline::CommitterConfig;
 use sui_indexer_alt_framework::pipeline::sequential::SequentialConfig;
 use sui_indexer_alt_framework::service::Service;

+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::config::IndexerConfig;
 use crate::config::OutputStoreConfig;
+use crate::handlers::system_package_eviction::SystemPackageEviction;
 use crate::metrics::Metrics;
-use crate::package_store::PackageCache;
 use crate::progress_monitoring::spawn_snowflake_monitors;
 use crate::store::AnalyticsStore;

@@ -55,31 +57,23 @@ pub async fn build_analytics_indexer(
         .find_checkpoint_range(indexer_args.first_checkpoint, indexer_args.last_checkpoint)
         .await?;

-    let work_dir = if let Some(ref work_dir) = config.work_dir {
-        tempfile::Builder::new()
-            .prefix("sui-analytics-indexer-")
-            .tempdir_in(work_dir)?
-            .keep()
-    } else {
-        tempfile::Builder::new()
-            .prefix("sui-analytics-indexer-")
-            .tempdir()?
-            .keep()
-    };
-
     let rpc_url = client_args
         .ingestion
         .rpc_api_url
         .as_ref()
         .map(|u| u.to_string())
         .unwrap_or_default();
-    let package_cache_path = work_dir.join("package_cache");
-    let package_cache = Arc::new(PackageCache::new(&package_cache_path, &rpc_url));
+    let package_cache = Arc::new(RpcPackageStore::new(&rpc_url).with_cache());
+
+    let mut pipeline_filter = indexer_args.pipeline;
+    if !pipeline_filter.is_empty() {
+        pipeline_filter.push("SystemPackageEviction".to_string());
+    }

     let adjusted_indexer_args = IndexerArgs {
         first_checkpoint: adjusted_first_checkpoint,
         last_checkpoint: adjusted_last_checkpoint,
-        pipeline: indexer_args.pipeline,
+        pipeline: pipeline_filter,
         task: indexer_args.task,
     };

@@ -113,12 +107,20 @@ pub async fn build_analytics_indexer(
                 &mut indexer,
                 pipeline_config,
                 package_cache.clone(),
+                &rpc_url,
                 metrics.clone(),
                 sequential,
             )
             .await?;
     }

+    indexer
+        .sequential_pipeline(
+            SystemPackageEviction::new(package_cache.clone()),
+            base_sequential.clone(),
+        )
+        .await?;
+
     // Spawn Snowflake monitors (if configured)
     let cancel = CancellationToken::new();
     let sf_handles = spawn_snowflake_monitors(&config, metrics, cancel.clone())?;
diff --git a/crates/sui-analytics-indexer/src/lib.rs b/crates/sui-analytics-indexer/src/lib.rs
index 6c6051519a56..c529132d152b 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/df.rs b/crates/sui-analytics-indexer/src/handlers/tables/df.rs
index 90bf7d7bf014..f7b1f2463afc 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/df.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/df.rs
@@ -24,17 +24,20 @@ use sui_types::object::bounded_visitor::BoundedVisitor;
 use tap::tap::TapFallible;
 use tracing::warn;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::DynamicFieldRow;

 pub struct DynamicFieldProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl DynamicFieldProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -56,9 +59,7 @@ impl DynamicFieldProcessor {
             return Ok(None);
         }

-        let layout = self
-            .package_cache
-            .resolver_for_epoch(epoch)
+        let layout = Resolver::new(self.package_cache.clone())
             .type_layout(move_object.type_().clone().into())
             .await?;
         let object_id = object.id();
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/event.rs b/crates/sui-analytics-indexer/src/handlers/tables/event.rs
index 9fbb4c98ac2e..547811179a86 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/event.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/event.rs
@@ -13,17 +13,20 @@ use sui_types::effects::TransactionEffectsAPI;
 use sui_types::event::Event;
 use sui_types::full_checkpoint_content::Checkpoint;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::EventRow;

 pub struct EventProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl EventProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -63,9 +66,7 @@ impl Processor for EventProcessor {
                         contents,
                     } = event;

-                    let layout = self
-                        .package_cache
-                        .resolver_for_epoch(epoch)
+                    let layout = Resolver::new(self.package_cache.clone())
                         .type_layout(move_core_types::language_storage::TypeTag::Struct(
                             Box::new(type_.clone()),
                         ))
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/object.rs b/crates/sui-analytics-indexer/src/handlers/tables/object.rs
index 8608e56294e5..b15012c9c2f6 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/object.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/object.rs
@@ -13,6 +13,12 @@ use sui_types::base_types::ObjectID;
 use sui_types::full_checkpoint_content::Checkpoint;
 use sui_types::object::Object;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_package_resolver::error::Error as ResolverError;
+use sui_rpc_api::Client;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
 use crate::handlers::tables::ObjectStatusTracker;
 use crate::handlers::tables::get_is_consensus;
@@ -21,25 +27,27 @@ use crate::handlers::tables::get_owner_address;
 use crate::handlers::tables::get_owner_type;
 use crate::handlers::tables::initial_shared_version;
 use crate::metrics::Metrics;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::ObjectRow;
 use crate::tables::ObjectStatus;

 pub struct ObjectProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+    rpc_client: Client,
     package_filter: Option<ObjectID>,
     metrics: Metrics,
 }

 impl ObjectProcessor {
     pub fn new(
-        package_cache: Arc<PackageCache>,
+        package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+        rpc_url: &str,
         package_filter: &Option<String>,
         metrics: Metrics,
     ) -> Self {
         Self {
             package_cache,
+            rpc_client: Client::new(rpc_url).expect("invalid rpc url"),
             package_filter: package_filter
                 .clone()
                 .map(|x| ObjectID::from_hex_literal(&x).unwrap()),
@@ -47,6 +55,22 @@ impl ObjectProcessor {
         }
     }

+    async fn get_original_package_id(
+        &self,
+        id: move_core_types::account_address::AccountAddress,
+    ) -> anyhow::Result<ObjectID> {
+        let object = self
+            .rpc_client
+            .clone()
+            .get_object(ObjectID::from(id))
+            .await
+            .map_err(|_| ResolverError::PackageNotFound(id))?;
+        let sui_types::object::Data::Package(p) = &object.data else {
+            return Err(ResolverError::NotAPackage(id).into());
+        };
+        Ok(p.original_package_id())
+    }
+
     async fn check_type_hierarchy(
         &self,
         type_tag: &TypeTag,
@@ -71,11 +95,21 @@ impl ObjectProcessor {
         }

         // Resolve original package IDs in parallel
-        let mut original_ids = JoinSet::new();
+        let mut original_ids: JoinSet<anyhow::Result<ObjectID>> = JoinSet::new();

         for id in package_ids {
-            let package_cache = self.package_cache.clone();
-            original_ids.spawn(async move { package_cache.get_original_package_id(id).await });
+            let client = self.rpc_client.clone();
+            original_ids.spawn(async move {
+                let object = client
+                    .clone()
+                    .get_object(ObjectID::from(id))
+                    .await
+                    .map_err(|_| ResolverError::PackageNotFound(id))?;
+                let sui_types::object::Data::Package(p) = &object.data else {
+                    anyhow::bail!("not a package: {id}");
+                };
+                Ok(p.original_package_id())
+            });
         }

         // Check if any resolved ID matches our target
@@ -104,12 +138,7 @@ impl ObjectProcessor {
             .struct_tag()
             .and_then(|tag| object.data.try_as_move().map(|mo| (tag, mo.contents())))
         {
-            match get_move_struct(
-                &tag,
-                contents,
-                &self.package_cache.resolver_for_epoch(epoch),
-            )
-            .await
+            match get_move_struct(&tag, contents, &Resolver::new(self.package_cache.clone())).await
             {
                 Ok(move_struct) => Some(move_struct),
                 Err(err)
@@ -150,10 +179,7 @@ impl ObjectProcessor {

         let is_match = if let Some(package_id) = self.package_filter {
             if let Some(object_type) = object_type {
-                let original_package_id = self
-                    .package_cache
-                    .get_original_package_id(package_id.into())
-                    .await?;
+                let original_package_id = self.get_original_package_id(package_id.into()).await?;

                 let type_tag: TypeTag = object_type.clone().into();
                 self.check_type_hierarchy(&type_tag, original_package_id)
diff --git a/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs b/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
index dd58c7f23878..e0cf24afec3a 100644
--- a/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs
@@ -10,19 +10,22 @@ use sui_indexer_alt_framework::pipeline::Processor;
 use sui_types::base_types::EpochId;
 use sui_types::full_checkpoint_content::Checkpoint;

+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_package_resolver::Resolver;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::Row;
 use crate::handlers::tables::get_move_struct;
 use crate::handlers::tables::parse_struct;
-use crate::package_store::PackageCache;
 use crate::pipeline::Pipeline;
 use crate::tables::WrappedObjectRow;

 pub struct WrappedObjectProcessor {
-    package_cache: Arc<PackageCache>,
+    package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
 }

 impl WrappedObjectProcessor {
-    pub fn new(package_cache: Arc<PackageCache>) -> Self {
+    pub fn new(package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>) -> Self {
         Self { package_cache }
     }
 }
@@ -58,7 +61,7 @@ impl Processor for WrappedObjectProcessor {
                     match get_move_struct(
                         &tag,
                         contents,
-                        &self.package_cache.resolver_for_epoch(epoch),
+                        &Resolver::new(self.package_cache.clone()),
                     )
                     .await
                     {
diff --git a/crates/sui-analytics-indexer/src/indexer.rs b/crates/sui-analytics-indexer/src/indexer.rs
index ef7684be2855..13504beba095 100644
--- a/crates/sui-analytics-indexer/src/indexer.rs
+++ b/crates/sui-analytics-indexer/src/indexer.rs
@@ -26,10 +26,12 @@ use sui_indexer_alt_framework::pipeline::CommitterConfig;
 use sui_indexer_alt_framework::pipeline::sequential::SequentialConfig;
 use sui_indexer_alt_framework::service::Service;

+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::config::IndexerConfig;
 use crate::config::OutputStoreConfig;
+use crate::handlers::system_package_eviction::SystemPackageEviction;
 use crate::metrics::Metrics;
-use crate::package_store::PackageCache;
 use crate::progress_monitoring::spawn_snowflake_monitors;
 use crate::store::AnalyticsStore;

@@ -55,31 +57,23 @@ pub async fn build_analytics_indexer(
         .find_checkpoint_range(indexer_args.first_checkpoint, indexer_args.last_checkpoint)
         .await?;

-    let work_dir = if let Some(ref work_dir) = config.work_dir {
-        tempfile::Builder::new()
-            .prefix("sui-analytics-indexer-")
-            .tempdir_in(work_dir)?
-            .keep()
-    } else {
-        tempfile::Builder::new()
-            .prefix("sui-analytics-indexer-")
-            .tempdir()?
-            .keep()
-    };
-
     let rpc_url = client_args
         .ingestion
         .rpc_api_url
         .as_ref()
         .map(|u| u.to_string())
         .unwrap_or_default();
-    let package_cache_path = work_dir.join("package_cache");
-    let package_cache = Arc::new(PackageCache::new(&package_cache_path, &rpc_url));
+    let package_cache = Arc::new(RpcPackageStore::new(&rpc_url).with_cache());
+
+    let mut pipeline_filter = indexer_args.pipeline;
+    if !pipeline_filter.is_empty() {
+        pipeline_filter.push("SystemPackageEviction".to_string());
+    }

     let adjusted_indexer_args = IndexerArgs {
         first_checkpoint: adjusted_first_checkpoint,
         last_checkpoint: adjusted_last_checkpoint,
-        pipeline: indexer_args.pipeline,
+        pipeline: pipeline_filter,
         task: indexer_args.task,
     };

@@ -113,12 +107,20 @@ pub async fn build_analytics_indexer(
                 &mut indexer,
                 pipeline_config,
                 package_cache.clone(),
+                &rpc_url,
                 metrics.clone(),
                 sequential,
             )
             .await?;
     }

+    indexer
+        .sequential_pipeline(
+            SystemPackageEviction::new(package_cache.clone()),
+            base_sequential.clone(),
+        )
+        .await?;
+
     // Spawn Snowflake monitors (if configured)
     let cancel = CancellationToken::new();
     let sf_handles = spawn_snowflake_monitors(&config, metrics, cancel.clone())?;
diff --git a/crates/sui-analytics-indexer/src/lib.rs b/crates/sui-analytics-indexer/src/lib.rs
index 6c6051519a56..c529132d152b 100644
--- a/crates/sui-analytics-indexer/src/lib.rs
+++ b/crates/sui-analytics-indexer/src/lib.rs
@@ -10,7 +10,6 @@ pub mod config;
 pub mod handlers;
 pub mod indexer;
 pub mod metrics;
-pub mod package_store;
 pub mod pipeline;
 pub mod progress_monitoring;
 pub mod schema;
diff --git a/crates/sui-analytics-indexer/src/package_store/mod.rs b/crates/sui-analytics-indexer/src/package_store/mod.rs
deleted file mode 100644
index 38c6b62e2063..000000000000
--- a/crates/sui-analytics-indexer/src/package_store/mod.rs
+++ /dev/null
@@ -1,233 +0,0 @@
-// Copyright (c) Mysten Labs, Inc.
-// SPDX-License-Identifier: Apache-2.0
-
-use std::num::NonZeroUsize;
-use std::ops::Deref;
-use std::path::Path;
-use std::result::Result as StdResult;
-use std::sync::Arc;
-use std::sync::Mutex;
-
-use async_trait::async_trait;
-use lru::LruCache;
-use move_core_types::account_address::AccountAddress;
-use sui_package_resolver::Package;
-use sui_package_resolver::PackageStore;
-use sui_package_resolver::PackageStoreWithLruCache;
-use sui_package_resolver::Resolver;
-use sui_package_resolver::Result;
-use sui_package_resolver::error::Error as ResolverError;
-use sui_rpc_api::Client;
-use sui_types::SYSTEM_PACKAGE_ADDRESSES;
-use sui_types::base_types::ObjectID;
-use sui_types::object::Data;
-use sui_types::object::Object;
-use thiserror::Error;
-use typed_store::DBMapUtils;
-use typed_store::Map;
-use typed_store::TypedStoreError;
-use typed_store::rocks::DBMap;
-use typed_store::rocks::MetricConf;
-
-const STORE: &str = "RocksDB";
-const MAX_EPOCH_CACHES: usize = 2; // keep at most two epochs in memory
-
-#[derive(Error, Debug)]
-pub enum Error {
-    #[error("{0}")]
-    TypedStore(#[from] TypedStoreError),
-    #[error("Package not found: {0}")]
-    PackageNotFound(AccountAddress),
-}
-
-impl From<Error> for ResolverError {
-    fn from(e: Error) -> Self {
-        ResolverError::Store {
-            store: STORE,
-            error: e.to_string(),
-        }
-    }
-}
-
-#[derive(DBMapUtils)]
-pub struct PackageStoreTables {
-    pub(crate) packages: DBMap<ObjectID, Object>,
-}
-
-impl PackageStoreTables {
-    pub fn new(path: &Path) -> Arc<Self> {
-        Arc::new(Self::open_tables_read_write(
-            path.to_path_buf(),
-            MetricConf::new("package"),
-            None,
-            None,
-        ))
-    }
-
-    fn update(&self, object: &Object) -> StdResult<(), Error> {
-        self.update_batch(std::iter::once(object))
-    }
-
-    fn update_batch<'a, I>(&self, objects: I) -> StdResult<(), Error>
-    where
-        I: IntoIterator<Item = &'a Object>,
-    {
-        let mut batch = self.packages.batch();
-        batch.insert_batch(&self.packages, objects.into_iter().map(|o| (o.id(), o)))?;
-
-        batch.write()?;
-        Ok(())
-    }
-}
-
-#[derive(Clone)]
-pub struct LocalDBPackageStore {
-    tables: Arc<PackageStoreTables>,
-    client: Client,
-}
-
-impl LocalDBPackageStore {
-    pub fn new(path: &Path, rpc_url: &str) -> Self {
-        Self {
-            tables: PackageStoreTables::new(path),
-            client: Client::new(rpc_url).expect("invalid rpc url"),
-        }
-    }
-
-    fn update(&self, object: &Object) -> StdResult<(), Error> {
-        if object.data.try_as_package().is_some() {
-            self.tables.update(object)?;
-        }
-        Ok(())
-    }
-
-    async fn get(&self, id: AccountAddress) -> StdResult<Object, Error> {
-        if let Some(o) = self.tables.packages.get(&ObjectID::from(id))? {
-            return Ok(o);
-        }
-        let o = self
-            .client
-            .clone()
-            .get_object(ObjectID::from(id))
-            .await
-            .map_err(|_| Error::PackageNotFound(id))?;
-        self.update(&o)?;
-        Ok(o)
-    }
-
-    pub async fn get_original_package_id(&self, id: AccountAddress) -> StdResult<ObjectID, Error> {
-        let o = self.get(id).await?;
-        let Data::Package(p) = &o.data else {
-            return Err(Error::TypedStore(TypedStoreError::SerializationError(
-                "not a package".into(),
-            )));
-        };
-        Ok(p.original_package_id())
-    }
-}
-
-#[async_trait]
-impl PackageStore for LocalDBPackageStore {
-    async fn fetch(&self, id: AccountAddress) -> Result<Arc<Package>> {
-        let o = self.get(id).await?;
-        Ok(Arc::new(Package::read_from_object(&o)?))
-    }
-}
-
-// A thin new‑type wrapper so we can hand an `Arc` to `Resolver`
-#[derive(Clone)]
-pub struct GlobalArcStore(pub Arc<PackageStoreWithLruCache<LocalDBPackageStore>>);
-
-#[async_trait]
-impl PackageStore for GlobalArcStore {
-    async fn fetch(&self, id: AccountAddress) -> Result<Arc<Package>> {
-        self.0.fetch(id).await
-    }
-}
-
-impl Deref for GlobalArcStore {
-    type Target = PackageStoreWithLruCache<LocalDBPackageStore>;
-    fn deref(&self) -> &Self::Target {
-        &self.0
-    }
-}
-
-// Multi-level cache. System packages can change across epochs while non-system packages are
-// immutable and can be cached across epochs. This impl assumes the system is at most working on
-// 2 epochs at a time (at the epoch boundary). When the indexer begins processing a new epoch it
-// will create a new PackageStoreWithLruCache for that epoch and the oldest epoch in the cache
-// will be dropped.
-#[derive(Clone)]
-pub struct CompositeStore {
-    pub epoch: u64,
-    pub global: Arc<PackageStoreWithLruCache<LocalDBPackageStore>>,
-    pub base: LocalDBPackageStore,
-    pub epochs: Arc<Mutex<LruCache<u64, Arc<PackageStoreWithLruCache<LocalDBPackageStore>>>>>,
-}
-
-impl CompositeStore {
-    /// Lazily obtain (or create) the cache for the current epoch.
-    fn epoch_cache(&self) -> Arc<PackageStoreWithLruCache<LocalDBPackageStore>> {
-        let mut caches = self.epochs.lock().unwrap();
-        if let Some(cache) = caches.get(&self.epoch) {
-            return cache.clone();
-        }
-        // Not present — create a fresh cache backed by the same LocalDB store.
-        let cache = Arc::new(PackageStoreWithLruCache::new(self.base.clone()));
-        caches.put(self.epoch, cache.clone());
-        cache
-    }
-}
-
-#[async_trait]
-impl PackageStore for CompositeStore {
-    async fn fetch(&self, id: AccountAddress) -> Result<Arc<Package>> {
-        if SYSTEM_PACKAGE_ADDRESSES.contains(&id) {
-            let cache = self.epoch_cache();
-            return cache.fetch(id).await;
-        }
-        self.global.fetch(id).await
-    }
-}
-
-// Top‑level cache façade
-pub struct PackageCache {
-    pub base_store: LocalDBPackageStore,
-    pub global_cache: Arc<PackageStoreWithLruCache<LocalDBPackageStore>>,
-    pub epochs: Arc<Mutex<LruCache<u64, Arc<PackageStoreWithLruCache<LocalDBPackageStore>>>>>,
-    pub resolver: Resolver<GlobalArcStore>,
-}
-
-impl PackageCache {
-    pub fn new(path: &Path, rpc_url: &str) -> Self {
-        let base_store = LocalDBPackageStore::new(path, rpc_url);
-        let global_cache = Arc::new(PackageStoreWithLruCache::new(base_store.clone()));
-        Self {
-            resolver: Resolver::new(GlobalArcStore(global_cache.clone())),
-            base_store,
-            global_cache,
-            epochs: Arc::new(Mutex::new(LruCache::new(
-                NonZeroUsize::new(MAX_EPOCH_CACHES).unwrap(),
-            ))),
-        }
-    }
-
-    pub fn resolver_for_epoch(&self, epoch: u64) -> Resolver<CompositeStore> {
-        Resolver::new(CompositeStore {
-            epoch,
-            global: self.global_cache.clone(),
-            base: self.base_store.clone(),
-            epochs: self.epochs.clone(),
-        })
-    }
-
-    #[cfg(not(test))]
-    pub async fn get_original_package_id(&self, id: AccountAddress) -> Result<ObjectID> {
-        Ok(self.base_store.get_original_package_id(id).await?)
-    }
-
-    #[cfg(test)]
-    pub async fn get_original_package_id(&self, id: AccountAddress) -> Result<ObjectID> {
-        Ok(id.into())
-    }
-}
diff --git a/crates/sui-analytics-indexer/src/pipeline.rs b/crates/sui-analytics-indexer/src/pipeline.rs
index 1a52e90d7e39..fbd3dae11a15 100644
--- a/crates/sui-analytics-indexer/src/pipeline.rs
+++ b/crates/sui-analytics-indexer/src/pipeline.rs
@@ -29,8 +29,10 @@ use crate::handlers::tables::TransactionBCSProcessor;
 use crate::handlers::tables::TransactionObjectsProcessor;
 use crate::handlers::tables::TransactionProcessor;
 use crate::handlers::tables::WrappedObjectProcessor;
+use sui_package_resolver::PackageStoreWithLruCache;
+use sui_rpc_resolver::package_store::RpcPackageStore;
+
 use crate::metrics::Metrics;
-use crate::package_store::PackageCache;
 use crate::store::AnalyticsStore;

 /// Register a sequential pipeline with the analytics handler.
@@ -125,7 +127,8 @@ impl Pipeline {
         &self,
         indexer: &mut Indexer<AnalyticsStore>,
         pipeline_config: &PipelineConfig,
-        package_cache: Arc<PackageCache>,
+        package_cache: Arc<PackageStoreWithLruCache<RpcPackageStore>>,
+        rpc_url: &str,
         metrics: Metrics,
         sequential_config: SequentialConfig,
     ) -> Result<()> {
@@ -156,6 +159,7 @@ impl Pipeline {
                     indexer,
                     ObjectProcessor::new(
                         package_cache.clone(),
+                        rpc_url,
                         &pipeline_config.package_id_filter,
                         metrics,
                     ),
diff --git a/crates/sui-analytics-indexer/src/store/mod.rs b/crates/sui-analytics-indexer/src/store/mod.rs
index 068fbd2bb950..eec956624a5c 100644
--- a/crates/sui-analytics-indexer/src/store/mod.rs
+++ b/crates/sui-analytics-indexer/src/store/mod.rs
@@ -655,7 +655,10 @@ impl Connection for AnalyticsConnection<'_> {
         &mut self,
         pipeline: &str,
     ) -> anyhow::Result<Option<CommitterWatermark>> {
-        let output_prefix = self.pipeline_config(pipeline).output_prefix().to_string();
+        let Some(config) = self.store.config.get_pipeline_config(pipeline) else {
+            return Ok(None);
+        };
+        let output_prefix = config.output_prefix().to_string();
         match &self.store.mode {
             StoreMode::Live(store) => store.committer_watermark(&output_prefix).await,
             StoreMode::Migration(store) => store.committer_watermark(&output_prefix).await,
PATCH

# Verify the patch applied successfully
echo "Patch applied successfully"
