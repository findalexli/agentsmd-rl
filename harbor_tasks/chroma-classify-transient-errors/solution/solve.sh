#!/bin/bash
set -e

cd /workspace/chroma

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 9954e0fc890..08221ea80d1 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -1875,6 +1875,7 @@ dependencies = [
  "chroma-tracing",
  "chroma-types",
  "futures",
+ "hyper 1.8.1",
  "opentelemetry 0.27.1",
  "proptest",
  "rand 0.8.5",
diff --git a/Cargo.toml b/Cargo.toml
index 9bb645eb67d..9b648b5dd13 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -19,6 +19,7 @@ flatbuffers = "25.2.10"
 futures = "0.3"
 futures-core = "0.3"
 http-body-util = "0.1.3"
+hyper = "1"
 object_store = { version = "0.12", features = ["gcp"] }
 lazy_static = { version = "1.4" }
 lexical-core = "1.0"
diff --git a/rust/error/src/lib.rs b/rust/error/src/lib.rs
index a4cc73ca8dd..06fd6373962 100644
--- a/rust/error/src/lib.rs
+++ b/rust/error/src/lib.rs
@@ -18,6 +18,21 @@ mod validator;
 #[cfg(feature = "validator")]
 pub use validator::*;

+/// Returns true when any error in the source chain satisfies `predicate`.
+pub fn source_chain_contains(
+    source: &(dyn Error + 'static),
+    mut predicate: impl FnMut(&(dyn Error + 'static)) -> bool,
+) -> bool {
+    let mut current = Some(source);
+    while let Some(err) = current {
+        if predicate(err) {
+            return true;
+        }
+        current = err.source();
+    }
+    false
+}
+
 #[derive(PartialEq, Debug, Clone, Copy)]
 pub enum ErrorCodes {
     // OK is returned on success, we use "Success" since Ok is a keyword in Rust.
@@ -147,3 +162,94 @@ impl ChromaError for std::io::Error {
         ErrorCodes::Unknown
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use std::{cell::Cell, error::Error, fmt};
+
+    use super::source_chain_contains;
+
+    #[derive(Debug)]
+    struct TestError {
+        message: &'static str,
+        source: Option<Box<dyn Error + Send + Sync + 'static>>,
+    }
+
+    impl TestError {
+        fn new(message: &'static str) -> Self {
+            Self {
+                message,
+                source: None,
+            }
+        }
+
+        fn with_source(message: &'static str, source: impl Error + Send + Sync + 'static) -> Self {
+            Self {
+                message,
+                source: Some(Box::new(source)),
+            }
+        }
+    }
+
+    impl fmt::Display for TestError {
+        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
+            write!(f, "{}", self.message)
+        }
+    }
+
+    impl Error for TestError {
+        fn source(&self) -> Option<&(dyn Error + 'static)> {
+            self.source
+                .as_deref()
+                .map(|err| err as &(dyn Error + 'static))
+        }
+    }
+
+    #[test]
+    fn source_chain_contains_matches_root_error() {
+        let err = TestError::new("root");
+
+        assert!(source_chain_contains(&err, |candidate| {
+            candidate.to_string() == "root"
+        }));
+    }
+
+    #[test]
+    fn source_chain_contains_matches_nested_source_error() {
+        let err = TestError::with_source(
+            "root",
+            TestError::with_source("middle", TestError::new("leaf")),
+        );
+
+        assert!(source_chain_contains(&err, |candidate| {
+            candidate.to_string() == "leaf"
+        }));
+    }
+
+    #[test]
+    fn source_chain_contains_returns_false_when_no_error_matches() {
+        let err = TestError::with_source(
+            "root",
+            TestError::with_source("middle", TestError::new("leaf")),
+        );
+
+        assert!(!source_chain_contains(&err, |candidate| {
+            candidate.to_string() == "missing"
+        }));
+    }
+
+    #[test]
+    fn source_chain_contains_stops_after_first_match() {
+        let err = TestError::with_source(
+            "root",
+            TestError::with_source("middle", TestError::new("leaf")),
+        );
+        let visits = Cell::new(0);
+
+        assert!(source_chain_contains(&err, |candidate| {
+            visits.set(visits.get() + 1);
+            candidate.to_string() == "middle"
+        }));
+        assert_eq!(2, visits.get());
+    }
+}
diff --git a/rust/log/Cargo.toml b/rust/log/Cargo.toml
index 69765f18e63..0cc1f11e4f9 100644
--- a/rust/log/Cargo.toml
+++ b/rust/log/Cargo.toml
@@ -18,6 +18,7 @@ serde_json = { workspace = true }
 bytemuck = { workspace = true }
 futures = { workspace = true }
 opentelemetry = { workspace = true }
+hyper = { workspace = true }

 chroma-tracing = { workspace = true, features = ["grpc"] }
 chroma-config = { workspace = true }
diff --git a/rust/log/src/grpc_log.rs b/rust/log/src/grpc_log.rs
index 262889fafd3..d322bac5f2e 100644
--- a/rust/log/src/grpc_log.rs
+++ b/rust/log/src/grpc_log.rs
@@ -6,7 +6,7 @@ use async_trait::async_trait;
 use chroma_config::assignment::assignment_policy::AssignmentPolicy;
 use chroma_config::registry::Registry;
 use chroma_config::Configurable;
-use chroma_error::{ChromaError, ErrorCodes};
+use chroma_error::{source_chain_contains, ChromaError, ErrorCodes};
 use chroma_memberlist::client_manager::{
     ClientAssigner, ClientAssignmentError, ClientManager, ClientOptions, Tier,
 };
@@ -39,6 +39,26 @@ fn backoff_reason_from_status(status: &tonic::Status) -> Option<&str> {
     status.metadata().get(BACKOFF_REASON_MD_KEY)?.to_str().ok()
 }

+fn is_retryable_transport_status(status: &tonic::Status) -> bool {
+    match status.code() {
+        tonic::Code::Unavailable => true,
+        tonic::Code::Cancelled => {
+            source_chain_contains(status, |err| err.is::<tonic::transport::Error>())
+                && source_chain_contains(status, |err| {
+                    err.downcast_ref::<hyper::Error>()
+                        .map(|hyper_err| {
+                            hyper_err.is_canceled()
+                                || hyper_err.is_closed()
+                                || hyper_err.is_incomplete_message()
+                                || hyper_err.is_timeout()
+                        })
+                        .unwrap_or(false)
+                })
+        }
+        _ => false,
+    }
+}
+
 //////////////// Errors ////////////////

 #[derive(Error, Debug)]
@@ -116,7 +136,13 @@ impl ChromaError for GrpcPushLogsError {
         match self {
             GrpcPushLogsError::Backoff => ErrorCodes::ResourceExhausted,
             GrpcPushLogsError::BackoffCompaction => ErrorCodes::ResourceExhausted,
-            GrpcPushLogsError::FailedToPushLogs(_) => ErrorCodes::Internal,
+            GrpcPushLogsError::FailedToPushLogs(status) => {
+                if is_retryable_transport_status(status) {
+                    ErrorCodes::Unavailable
+                } else {
+                    status.code().into()
+                }
+            }
             GrpcPushLogsError::ConversionError(_) => ErrorCodes::Internal,
             GrpcPushLogsError::Sealed => ErrorCodes::FailedPrecondition,
             GrpcPushLogsError::ClientAssignerError(e) => e.code(),
@@ -781,6 +807,26 @@ mod tests {
     use super::*;
     use chroma_types::chroma_proto::CollectionInfo as ProtoCollectionInfo;

+    #[test]
+    fn grpc_push_logs_unavailable_stays_unavailable() {
+        let status = tonic::Status::unavailable("transport unavailable");
+
+        assert_eq!(
+            GrpcPushLogsError::FailedToPushLogs(status).code(),
+            ErrorCodes::Unavailable
+        );
+    }
+
+    #[test]
+    fn grpc_push_logs_plain_cancelled_stays_cancelled() {
+        let status = tonic::Status::cancelled("cancelled by caller");
+
+        assert_eq!(
+            GrpcPushLogsError::FailedToPushLogs(status).code(),
+            ErrorCodes::Cancelled
+        );
+    }
+
     #[test]
     fn post_process_get_all_returns_smaller_first_log_offset() {
         let collection_id = "12345678-1234-1234-1234-123456789abc";
diff --git a/rust/storage/src/object_storage.rs b/rust/storage/src/object_storage.rs
index a8206a7474e..01841da01a5 100644
--- a/rust/storage/src/object_storage.rs
+++ b/rust/storage/src/object_storage.rs
@@ -3,13 +3,12 @@
 //!
 //! ## ETag Implementation Note
 //! The `UpdateVersion` struct is serialized to JSON and stored as an ETag string.
-use std::sync::Arc;
-use std::time::Duration;
+use std::{error::Error as StdError, sync::Arc, time::Duration};

 use async_trait::async_trait;
 use bytes::{Bytes, BytesMut};
 use chroma_config::{registry::Registry, Configurable};
-use chroma_error::ChromaError;
+use chroma_error::{source_chain_contains, ChromaError};
 use chroma_tracing::util::Stopwatch;
 use chroma_types::Cmek;
 use futures::stream::{self, StreamExt, TryStreamExt};
@@ -31,6 +30,26 @@ use crate::{
 };

 const GCP_CMEK_HEADER: &str = "x-goog-encryption-kms-key-name";
+const GCS_STORE_NAME: &str = "GCS";
+const GCS_TOO_MANY_REQUESTS_MESSAGE: &str =
+    "Server returned non-2xx status code: 429 Too Many Requests";
+const GCS_SLOWDOWN_CODE: &str = "<Code>SlowDown</Code>";
+const GCS_MUTATION_RATE_LIMIT_MESSAGE: &str = "rate limit for object mutation operations";
+
+fn is_gcs_backoff_message(message: &str) -> bool {
+    // object_store wraps GCS status/body failures in private retry types, so the
+    // formatted status/body text is the only stable signal exposed here.
+    //
+    // TODO(rescrv):  When object store gives a better error, match on something other than strings
+    message.contains(GCS_TOO_MANY_REQUESTS_MESSAGE)
+        || message.contains(GCS_SLOWDOWN_CODE)
+        || message.contains(GCS_MUTATION_RATE_LIMIT_MESSAGE)
+}
+
+fn is_gcs_backoff_error(store: &'static str, source: &(dyn StdError + 'static)) -> bool {
+    store == GCS_STORE_NAME
+        && source_chain_contains(source, |err| is_gcs_backoff_message(&err.to_string()))
+}

 #[derive(Debug)]
 struct HttpClientWrapper {
@@ -104,9 +123,15 @@ impl From<object_store::Error> for StorageError {
             object_store::Error::InvalidPath { source } => StorageError::Generic {
                 source: Arc::new(source),
             },
-            err @ object_store::Error::Generic { .. } => StorageError::Generic {
-                source: Arc::new(err),
-            },
+            object_store::Error::Generic { store, source } => {
+                if is_gcs_backoff_error(store, source.as_ref()) {
+                    StorageError::Backoff
+                } else {
+                    StorageError::Generic {
+                        source: Arc::new(object_store::Error::Generic { store, source }),
+                    }
+                }
+            }
             object_store::Error::JoinError { source } => StorageError::Generic {
                 source: Arc::new(source),
             },
@@ -120,6 +145,121 @@ impl From<object_store::Error> for StorageError {
     }
 }

+#[cfg(test)]
+mod tests {
+    use std::{error::Error as StdError, fmt};
+
+    use super::*;
+
+    #[derive(Debug)]
+    struct FakeError {
+        message: &'static str,
+        source: Option<Box<dyn StdError + Send + Sync + 'static>>,
+    }
+
+    impl FakeError {
+        fn new(message: &'static str) -> Self {
+            Self {
+                message,
+                source: None,
+            }
+        }
+
+        fn with_source(
+            message: &'static str,
+            source: impl StdError + Send + Sync + 'static,
+        ) -> Self {
+            Self {
+                message,
+                source: Some(Box::new(source)),
+            }
+        }
+    }
+
+    impl fmt::Display for FakeError {
+        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
+            write!(f, "{}", self.message)
+        }
+    }
+
+    impl StdError for FakeError {
+        fn source(&self) -> Option<&(dyn StdError + 'static)> {
+            self.source
+                .as_deref()
+                .map(|err| err as &(dyn StdError + 'static))
+        }
+    }
+
+    fn generic_store_error(
+        store: &'static str,
+        source: impl StdError + Send + Sync + 'static,
+    ) -> object_store::Error {
+        object_store::Error::Generic {
+            store,
+            source: Box::new(source),
+        }
+    }
+
+    fn gcs_generic_error(source: impl StdError + Send + Sync + 'static) -> object_store::Error {
+        generic_store_error(GCS_STORE_NAME, source)
+    }
+
+    #[test]
+    fn test_gcs_generic_429_maps_to_backoff() {
+        let err = gcs_generic_error(FakeError::new(
+            "Server returned non-2xx status code: 429 Too Many Requests",
+        ));
+
+        assert!(matches!(StorageError::from(err), StorageError::Backoff));
+    }
+
+    #[test]
+    fn test_gcs_generic_slowdown_in_source_chain_maps_to_backoff() {
+        let err = gcs_generic_error(FakeError::with_source(
+            "retry exhausted",
+            FakeError::new(
+                "<?xml version='1.0'?><Error><Code>SlowDown</Code><Message>Please reduce your request rate.</Message></Error>",
+            ),
+        ));
+
+        assert!(matches!(StorageError::from(err), StorageError::Backoff));
+    }
+
+    #[test]
+    fn test_gcs_generic_mutation_rate_limit_message_maps_to_backoff() {
+        let err = gcs_generic_error(FakeError::new(
+            "Quota exceeded: rate limit for object mutation operations",
+        ));
+
+        assert!(matches!(StorageError::from(err), StorageError::Backoff));
+    }
+
+    #[test]
+    fn test_gcs_generic_non_throttling_error_stays_generic() {
+        let err = gcs_generic_error(FakeError::new(
+            "Server returned non-2xx status code: 503 Service Unavailable",
+        ));
+
+        assert!(matches!(
+            StorageError::from(err),
+            StorageError::Generic { .. }
+        ));
+    }
+
+    #[test]
+    fn test_non_gcs_429_stays_generic() {
+        let err = generic_store_error(
+            "Azure",
+            FakeError::new("Server returned non-2xx status code: 429 Too Many Requests"),
+        );
+
+        assert!(matches!(
+            StorageError::from(err),
+            StorageError::Generic { .. }
+        ));
+    }
+}
+
 /// Serializable wrapper for UpdateVersion
 #[derive(Debug, Clone, Serialize, Deserialize)]
 struct ObjectVersionTag {
PATCH

# Idempotency check: verify distinctive line from patch
if ! grep -q "source_chain_contains" /workspace/chroma/rust/error/src/lib.rs; then
    echo "Patch not applied: source_chain_contains function not found"
    exit 1
fi

echo "Patch applied successfully"
