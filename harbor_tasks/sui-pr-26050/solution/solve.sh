#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied (idempotency check)
if grep -q "pub stream: Peekable<BoxStream<'static, Result<Checkpoint>>>" crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs b/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
index 12bcfe25cb31..d111449937b7 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
@@ -9,6 +9,7 @@ use std::time::Duration;
 use anyhow::Context;
 use anyhow::anyhow;
 use futures::Stream;
+use futures::TryStreamExt;
 use futures::future::try_join_all;
 use sui_futures::service::Service;
 use sui_futures::stream::Break;
@@ -291,32 +292,21 @@ where
         (noop_streaming_task(ingestion_end), ingestion_end)
     };

-    // Wrap the stream with a statement timeout to prevent hanging indefinitely, and then make it
-    // peekable.
-    let CheckpointStream { stream, chain_id } = match streaming_client.connect().await {
+    let CheckpointStream {
+        mut stream,
+        chain_id,
+    } = match streaming_client.connect().await {
         Ok(checkpoint_stream) => checkpoint_stream,
         Err(e) => {
             return fallback(&format!("Streaming connection failed: {e}"));
         }
     };

-    let mut checkpoint_envelope_stream = Box::pin(
-        stream
-            .timeout(config.streaming_statement_timeout())
-            .map(move |result| {
-                result
-                    .map_err(|_| Error::StreamingError(anyhow!("Connection timeout")))
-                    .flatten()
-                    .map(|checkpoint| CheckpointEnvelope {
-                        checkpoint: Arc::new(checkpoint),
-                        chain_id,
-                    })
-            }),
-    )
-    .peekable();
-
-    let checkpoint_envelope = match checkpoint_envelope_stream.peek().await {
-        Some(Ok(checkpoint_envelope)) => checkpoint_envelope,
+    let checkpoint_envelope = match std::pin::Pin::new(&mut stream).peek().await {
+        Some(Ok(checkpoint)) => CheckpointEnvelope {
+            checkpoint: Arc::new(checkpoint.clone()),
+            chain_id,
+        },
         Some(Err(e)) => {
             return fallback(&format!("Failed to peek latest checkpoint: {e}"));
         }
@@ -343,10 +333,14 @@ where
         checkpoint_hi, "Within buffer size, starting streaming"
     );

+    let envelope_stream = stream.map_ok(move |checkpoint| CheckpointEnvelope {
+        checkpoint: Arc::new(checkpoint),
+        chain_id,
+    });
     let stream_guard = TaskGuard::new(tokio::spawn(stream_and_broadcast_range(
         network_latest_cp.max(checkpoint_hi),
         end_cp,
-        checkpoint_envelope_stream,
+        envelope_stream,
         subscribers.clone(),
         ingest_hi_rx,
         metrics.clone(),
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/mod.rs b/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
index a1e2e04f5e74..6730049f0687 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
@@ -117,10 +117,13 @@ impl IngestionService {
     ) -> Result<Self> {
         let metrics = IngestionMetrics::new(metrics_prefix, registry);
         let ingestion_client = IngestionClient::new(args.ingestion, metrics.clone())?;
-        let streaming_client = args
-            .streaming
-            .streaming_url
-            .map(|uri| GrpcStreamingClient::new(uri, config.streaming_connection_timeout()));
+        let streaming_client = args.streaming.streaming_url.map(|uri| {
+            GrpcStreamingClient::new(
+                uri,
+                config.streaming_connection_timeout(),
+                config.streaming_statement_timeout(),
+            )
+        });

         let subscribers = Vec::new();
         let (commit_hi_tx, commit_hi_rx) = mpsc::unbounded_channel();
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
index ab8c064a9f98..0568bc0eb524 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
@@ -1,14 +1,14 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0

-use std::pin::Pin;
 use std::time::Duration;

 use anyhow::Context;
 use anyhow::anyhow;
 use async_trait::async_trait;
-use futures::Stream;
 use futures::StreamExt;
+use futures::stream::BoxStream;
+use futures::stream::Peekable;
 use sui_rpc::headers::X_SUI_CHAIN_ID;
 use sui_rpc::proto::sui::rpc::v2::SubscribeCheckpointsRequest;
 use sui_rpc::proto::sui::rpc::v2::subscription_service_client::SubscriptionServiceClient;
@@ -24,7 +24,7 @@ use crate::ingestion::error::Result;
 use crate::types::full_checkpoint_content::Checkpoint;

 pub struct CheckpointStream {
-    pub stream: Pin<Box<dyn Stream<Item = Result<Checkpoint>> + Send>>,
+    pub stream: Peekable<BoxStream<'static, Result<Checkpoint>>>,
     pub chain_id: ChainIdentifier,
 }

@@ -46,13 +46,15 @@ pub struct StreamingClientArgs {
 pub struct GrpcStreamingClient {
     uri: Uri,
     connection_timeout: Duration,
+    statement_timeout: Duration,
 }

 impl GrpcStreamingClient {
-    pub fn new(uri: Uri, connection_timeout: Duration) -> Self {
+    pub fn new(uri: Uri, connection_timeout: Duration, statement_timeout: Duration) -> Self {
         Self {
             uri,
             connection_timeout,
+            statement_timeout,
         }
     }
 }
@@ -85,7 +87,7 @@ impl CheckpointStreamingClient for GrpcStreamingClient {
             .map_err(|e| Error::StreamingError(anyhow!("Chain ID parse error: {e}")))?
             .into();

-        let converted_stream = response.into_inner().map(|result| match result {
+        let stream = response.into_inner().map(|result| match result {
             Ok(response) => response
                 .checkpoint
                 .context("Checkpoint data missing in response")
@@ -95,21 +97,39 @@ impl CheckpointStreamingClient for GrpcStreamingClient {
                 .map_err(Error::StreamingError),
             Err(e) => Err(Error::RpcClientError(e)),
         });
+        let stream = wrap_stream(stream, self.statement_timeout);

-        Ok(CheckpointStream {
-            stream: Box::pin(converted_stream),
-            chain_id,
-        })
+        Ok(CheckpointStream { stream, chain_id })
     }
 }

+/// Wraps a stream with a per-item timeout. Converts the resulting `Err(Elapsed)` into
+/// `Err(StreamingError)` if it occurs.
+fn wrap_stream(
+    stream: impl futures::Stream<Item = Result<Checkpoint>> + Send + 'static,
+    statement_timeout: Duration,
+) -> Peekable<BoxStream<'static, Result<Checkpoint>>> {
+    tokio_stream::StreamExt::timeout(stream, statement_timeout)
+        .map(move |result| match result {
+            Err(_elapsed) => Err(Error::StreamingError(anyhow!(
+                "Statement timeout after {statement_timeout:?}"
+            ))),
+            Ok(result) => result,
+        })
+        .boxed()
+        .peekable()
+}
+
 #[cfg(test)]
 pub mod test_utils {
+    use std::pin::Pin;
     use std::sync::Arc;
     use std::sync::Mutex;
     use std::time::Duration;
     use std::time::Instant;

+    use futures::Stream;
+
     use crate::types::test_checkpoint_data_builder::TestCheckpointBuilder;

     use super::*;
@@ -180,7 +200,10 @@ pub mod test_utils {
         actions: Arc<Mutex<Vec<StreamAction>>>,
         connection_failures_remaining: usize,
         connection_timeouts_remaining: usize,
+        /// How long mock timeout actions hang (must be > statement_timeout for timeouts to fire).
         timeout_duration: Duration,
+        /// Statement timeout applied to the stream wrapper.
+        statement_timeout: Duration,
     }

     impl MockStreamingClient {
@@ -192,6 +215,7 @@ pub mod test_utils {
         where
             I: IntoIterator<Item = u64>,
         {
+            let timeout_duration = timeout_duration.unwrap_or(Duration::from_secs(5));
             Self {
                 actions: Arc::new(Mutex::new(
                     checkpoint_range
@@ -201,7 +225,8 @@ pub mod test_utils {
                 )),
                 connection_failures_remaining: 0,
                 connection_timeouts_remaining: 0,
-                timeout_duration: timeout_duration.unwrap_or(Duration::from_secs(5)),
+                statement_timeout: timeout_duration / 2,
+                timeout_duration,
             }
         }

@@ -268,12 +293,11 @@ pub mod test_utils {
                     "Mock connection failure"
                 )));
             }
-            let stream = Box::pin(MockStreamState {
+            let stream_state = MockStreamState {
                 actions: Arc::clone(&self.actions),
-            });
-
+            };
             Ok(CheckpointStream {
-                stream,
+                stream: wrap_stream(stream_state, self.statement_timeout),
                 chain_id: Self::mock_chain_id(),
             })
         }
PATCH

echo "Patch applied successfully"
