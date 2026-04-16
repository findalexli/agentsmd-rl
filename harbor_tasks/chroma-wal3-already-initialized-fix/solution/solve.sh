#!/bin/bash
set -e

cd /workspace/chroma

# Idempotency check: verify if patch is already applied
# Check for the distinctive line from the gold patch
if grep -q "return Err(Error::AlreadyInitialized);" rust/wal3/src/interfaces/repl/manifest_manager.rs; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/rust/wal3/src/interfaces/repl/manifest_manager.rs b/rust/wal3/src/interfaces/repl/manifest_manager.rs
index 8de3104d988..b373a102834 100644
--- a/rust/wal3/src/interfaces/repl/manifest_manager.rs
+++ b/rust/wal3/src/interfaces/repl/manifest_manager.rs
@@ -137,7 +137,7 @@ impl ManifestManager {
                 Err(google_cloud_spanner::session::SessionError::GRPC(ref status))
                     if status.code() == Code::AlreadyExists =>
                 {
-                    return Err(Error::LogContentionRetry);
+                    return Err(Error::AlreadyInitialized);
                 }
                 Err(google_cloud_spanner::session::SessionError::GRPC(ref status))
                     if status.code() == Code::Aborted =>
diff --git a/rust/wal3/tests/repl_02_initialized_init_again.rs b/rust/wal3/tests/repl_02_initialized_init_again.rs
index 366cd80ad25..762977cfe39 100644
--- a/rust/wal3/tests/repl_02_initialized_init_again.rs
+++ b/rust/wal3/tests/repl_02_initialized_init_again.rs
@@ -2,7 +2,9 @@ use std::sync::Arc;

 use uuid::Uuid;

-use wal3::{Manifest, ManifestConsumer, ManifestManagerFactory, ReplicatedManifestManagerFactory};
+use wal3::{
+    Error, Manifest, ManifestConsumer, ManifestManagerFactory, ReplicatedManifestManagerFactory,
+};

 mod common;
 use common::setup_spanner_client;
@@ -50,8 +52,8 @@ async fn test_k8s_mcmr_integration_repl_02_initialized_init_again() {
         .init_manifest(&Manifest::new_empty("second"))
         .await;
     assert!(
-        result.is_err(),
-        "second init should fail for duplicate log_id"
+        matches!(result, Err(Error::AlreadyInitialized)),
+        "second init should fail with AlreadyInitialized for duplicate log_id, got {result:?}"
     );

     // Verify manifest still has first writer's data (unchanged).
diff --git a/rust/wal3/tests/repl_06_parallel_open_or_initialize.rs b/rust/wal3/tests/repl_06_parallel_open_or_initialize.rs
new file mode 100644
index 00000000000..fe9ad5e3ee6
--- /dev/null
+++ b/rust/wal3/tests/repl_06_parallel_open_or_initialize.rs
@@ -0,0 +1,70 @@
+use std::sync::atomic::{AtomicBool, Ordering};
+use std::sync::Arc;
+
+use chroma_storage::s3_client_for_test_with_new_bucket;
+use uuid::Uuid;
+
+use wal3::{create_repl_factories, LogWriter, LogWriterOptions, StorageWrapper};
+
+mod common;
+use common::{default_repl_options, setup_spanner_client};
+
+#[tokio::test]
+async fn test_k8s_mcmr_integration_repl_06_parallel_open_or_initialize() {
+    // Multiple concurrent open_or_initialize calls on an uninitialized repl log should all
+    // succeed. This exercises the race where one writer wins init and the others must treat
+    // AlreadyInitialized as success.
+    let client = setup_spanner_client().await;
+    let log_id = Uuid::new_v4();
+    let storage = s3_client_for_test_with_new_bucket().await;
+    let prefix = format!("repl_06_parallel_open_or_initialize/{log_id}");
+    let storages = Arc::new(vec![StorageWrapper::new(
+        "test-region".to_string(),
+        storage,
+        prefix,
+    )]);
+    let num_writers = 32;
+    let done = Arc::new(AtomicBool::new(false));
+    let notifier = Arc::new(tokio::sync::Notify::new());
+    let mut handles = Vec::with_capacity(num_writers);
+
+    for i in 0..num_writers {
+        let client = Arc::clone(&client);
+        let storages = Arc::clone(&storages);
+        let done = Arc::clone(&done);
+        let notifier = Arc::clone(&notifier);
+        handles.push(tokio::spawn(async move {
+            let writer_name = format!("writer{i}");
+            let (fragment_factory, manifest_factory) = create_repl_factories(
+                LogWriterOptions::default(),
+                default_repl_options(),
+                0,
+                storages,
+                client,
+                vec!["test-region".to_string()],
+                log_id,
+            );
+            if !done.load(Ordering::Relaxed) {
+                notifier.notified().await;
+            }
+            notifier.notify_one();
+            LogWriter::open_or_initialize(
+                LogWriterOptions::default(),
+                &writer_name,
+                fragment_factory,
+                manifest_factory,
+                None,
+            )
+            .await
+            .expect("open_or_initialize should succeed even when racing")
+        }));
+    }
+
+    done.store(true, Ordering::Relaxed);
+    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
+    notifier.notify_waiters();
+    for handle in handles {
+        notifier.notify_one();
+        handle.await.expect("task should not panic");
+    }
+}
PATCH

echo "Gold patch applied successfully"
