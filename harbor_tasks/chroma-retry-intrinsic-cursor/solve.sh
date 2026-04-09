#!/bin/bash
set -e

cd /workspace/chroma

# Apply the gold patch for adding retry logic to update_intrinsic_cursor
cat <<'PATCH' | git apply -
diff --git a/Cargo.lock b/Cargo.lock
index 28e0456506e..670fad9d108 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -1858,6 +1858,7 @@ version = "0.1.0"
 dependencies = [
  "arrow",
  "async-trait",
+ "backon",
  "bytes",
  "chroma-cache",
  "chroma-config",
diff --git a/rust/log-service/Cargo.toml b/rust/log-service/Cargo.toml
index 2c8ed9733f2..34b24ba3688 100644
--- a/rust/log-service/Cargo.toml
+++ b/rust/log-service/Cargo.toml
@@ -11,6 +11,7 @@ path = "src/bin/log.rs"
 arrow = { workspace = true }
 async-trait = { workspace = true }
 bytes = { workspace = true }
+backon = { workspace = true }
 parquet = { workspace = true }
 prost = { workspace = true }
 figment = { workspace = true }
diff --git a/rust/log-service/src/lib.rs b/rust/log-service/src/lib.rs
index b8d331550ac..cee0b4744e9 100644
--- a/rust/log-service/src/lib.rs
+++ b/rust/log-service/src/lib.rs
@@ -8,6 +8,7 @@ use std::sync::atomic::{AtomicU64, Ordering};
 use std::sync::Arc;
 use std::time::{Duration, Instant, SystemTime};

+use backon::{ExponentialBuilder, Retryable};
 use chroma_cache::CacheConfig;
 use chroma_config::helpers::{deserialize_duration_from_seconds, serialize_duration_to_seconds};
 use chroma_config::spanner::{SpannerChannelConfig, SpannerConfig, SpannerSessionPoolConfig};
@@ -1327,20 +1328,45 @@ impl LogServer {
             .map_err(|_| wal3::Error::internal(file!(), line!()))
             .unwrap()
             .as_micros() as u64;
-        let witness = log_reader
-            .update_intrinsic_cursor(
-                LogPosition::from_offset(adjusted_log_offset as u64),
-                epoch_us,
-                &self.config.my_member_id,
-                allow_rollback,
+        let log_reader = log_reader.clone();
+        let writer = self.config.my_member_id.clone();
+        let witness = (|| {
+            let log_reader = log_reader.clone();
+            let writer = writer.clone();
+            async move {
+                log_reader
+                    .update_intrinsic_cursor(
+                        LogPosition::from_offset(adjusted_log_offset as u64),
+                        epoch_us,
+                        &writer,
+                        allow_rollback,
+                    )
+                    .await
+            }
+        })
+        .retry(
+            ExponentialBuilder::new()
+                .with_min_delay(Duration::from_millis(20))
+                .with_max_delay(Duration::from_millis(200))
+                .with_max_times(3),
+        )
+        .when(|err: &wal3::Error| {
+            matches!(
+                err,
+                wal3::Error::StorageError(storage_error)
+                    if matches!(
+                        storage_error.as_ref(),
+                        chroma_storage::StorageError::Precondition { .. }
+                    )
             )
-            .await
-            .map_err(|err| {
-                Status::new(
-                    err.code().into(),
-                    format!("Failed to update intrinsic cursor: {}", err),
-                )
-            })?;
+        })
+        .await
+        .map_err(|err: wal3::Error| {
+            Status::new(
+                err.code().into(),
+                format!("Failed to update intrinsic cursor: {}", err),
+            )
+        })?;
         let Some(witness) = witness else {
             return Ok(Response::new(UpdateCollectionLogOffsetResponse {}));
         };
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "with_min_delay(Duration::from_millis(20))" rust/log-service/src/lib.rs && echo "Patch applied successfully"
