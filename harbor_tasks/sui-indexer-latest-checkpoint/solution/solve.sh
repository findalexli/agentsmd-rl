#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for PR #26116
patch -p1 << 'PATCH'
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs b/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
index 0058ccb6493c0..0e8c72725c3ab 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs
@@ -481,6 +481,10 @@ mod tests {
                 let bytes = test_checkpoint_data(checkpoint);
                 Ok(decode::checkpoint(&bytes).unwrap())
             }
+
+            async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+                Ok(0)
+            }
         }

         IngestionClient::new_impl(Arc::new(MockClient), metrics)
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/error.rs b/crates/sui-indexer-alt-framework/src/ingestion/error.rs
index 5d71fb31de2a7..610679f0a0edb 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/error.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/error.rs
@@ -17,6 +17,9 @@ pub enum Error {
     #[error("Failed to fetch chain id for checkpoint {0}: {1}")]
     ChainIdError(u64, #[source] anyhow::Error),

+    #[error("Failed to fetch latest checkpoint: {0}")]
+    LatestCheckpointError(#[source] anyhow::Error),
+
     #[error(transparent)]
     ObjectStoreError(#[from] object_store::Error),

diff --git a/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
index 7188f5cb7ea2b..7650e0c08115b 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
@@ -54,6 +54,8 @@ pub(crate) trait IngestionClientTrait: Send + Sync {
     async fn chain_id(&self) -> anyhow::Result<ChainIdentifier>;

     async fn checkpoint(&self, checkpoint: u64) -> CheckpointResult;
+
+    async fn latest_checkpoint_number(&self) -> anyhow::Result<u64>;
 }

 #[derive(clap::Args, Clone, Debug)]
@@ -393,10 +395,14 @@ impl IngestionClient {
             chain_id: *chain_id,
         })
     }
+
+    pub async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+        self.client.latest_checkpoint_number().await
+    }
 }

 /// Keep backing off until we are waiting for the max interval, but don't give up.
-fn transient_backoff() -> ExponentialBackoff {
+pub(crate) fn transient_backoff() -> ExponentialBackoff {
     ExponentialBackoff {
         max_interval: MAX_TRANSIENT_RETRY_INTERVAL,
         max_elapsed_time: None,
@@ -406,7 +412,7 @@ fn transient_backoff() -> ExponentialBackoff {

 /// Retry a fallible async operation with exponential backoff and slow-operation monitoring.
 /// Records the total time (including retries) in the provided latency histogram.
-async fn retry_transient_with_slow_monitor<F, Fut, T>(
+pub(crate) async fn retry_transient_with_slow_monitor<F, Fut, T>(
     operation: &str,
     make_future: F,
     latency: &Histogram,
@@ -536,6 +542,10 @@ mod tests {
                 .cloned()
                 .ok_or(CheckpointError::NotFound)
         }
+
+        async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+            Ok(0)
+        }
     }

     fn setup_test() -> (IngestionClient, Arc<MockIngestionClient>) {
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/mod.rs b/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
index 2aa87ae56a251..247442d03aed3 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/mod.rs
@@ -14,6 +14,7 @@ use serde::Deserialize;
 use serde::Serialize;
 use sui_futures::service::Service;
 use tokio::sync::mpsc;
+use tracing::warn;

 pub use crate::config::ConcurrencyConfig as IngestConcurrencyConfig;
 use crate::ingestion::broadcaster::broadcaster;
@@ -22,10 +23,14 @@ use crate::ingestion::error::Result;
 use crate::ingestion::ingestion_client::CheckpointEnvelope;
 use crate::ingestion::ingestion_client::IngestionClient;
 use crate::ingestion::ingestion_client::IngestionClientArgs;
+use crate::ingestion::streaming_client::CheckpointStream;
+use crate::ingestion::streaming_client::CheckpointStreamingClient;
 use crate::ingestion::streaming_client::GrpcStreamingClient;
 use crate::ingestion::streaming_client::StreamingClientArgs;
 use crate::metrics::IngestionMetrics;

+use self::ingestion_client::retry_transient_with_slow_monitor;
+
 mod broadcaster;
 mod byte_count;
 pub(crate) mod decode;
@@ -39,6 +44,8 @@ mod test_utils;

 pub(crate) const MAX_GRPC_MESSAGE_SIZE_BYTES: usize = 128 * 1024 * 1024;

+const OPERATION: &str = "latest_checkpoint_number";
+
 /// Combined arguments for both ingestion and streaming clients.
 /// This is a convenience wrapper that flattens both argument types.
 #[derive(clap::Args, Clone, Debug, Default)]
@@ -144,6 +151,26 @@ impl IngestionService {
         &self.ingestion_client
     }

+    pub async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+        let streaming_client = self.streaming_client.clone();
+        let ingestion_client = self.ingestion_client.clone();
+        let future = move || {
+            let mut streaming_client = streaming_client.clone();
+            let ingestion_client = ingestion_client.clone();
+            async move {
+                latest_checkpoint_number(&mut streaming_client, &ingestion_client)
+                    .await
+                    .map_err(|e| backoff::Error::transient(Error::LatestCheckpointError(e)))
+            }
+        };
+        Ok(retry_transient_with_slow_monitor(
+            OPERATION,
+            future,
+            &self.metrics.ingested_latest_checkpoint_latency,
+        )
+        .await?)
+    }
+
     /// Access to the ingestion metrics.
     pub(crate) fn metrics(&self) -> &Arc<IngestionMetrics> {
         &self.metrics
@@ -242,6 +269,42 @@ impl Default for IngestionConfig {
     }
 }

+/// Try to get the latest checkpoint number from the streaming client first, falling back to
+/// the ingestion client if the streaming client is unavailable or fails.
+async fn latest_checkpoint_number(
+    streaming_client: &mut Option<impl CheckpointStreamingClient>,
+    ingestion_client: &IngestionClient,
+) -> anyhow::Result<u64> {
+    if let Some(streaming_client) = streaming_client.as_mut() {
+        match streaming_client.connect().await {
+            Ok(CheckpointStream { mut stream, .. }) => match stream.peek().await {
+                Some(Ok(checkpoint)) => {
+                    return Ok(checkpoint.summary.sequence_number);
+                }
+                Some(Err(e)) => {
+                    warn!(
+                        operation = OPERATION,
+                        "Failed to peek checkpoint stream: {e}"
+                    );
+                }
+                None => {
+                    warn!(
+                        operation = OPERATION,
+                        "Checkpoint stream ended unexpectedly"
+                    );
+                }
+            },
+            Err(e) => {
+                warn!(
+                    operation = OPERATION,
+                    "Failed to connect streaming client: {e}"
+                );
+            }
+        }
+    }
+    ingestion_client.latest_checkpoint_number().await
+}
+
 #[cfg(test)]
 mod tests {
     use std::sync::Mutex;
@@ -252,13 +315,40 @@ mod tests {
     use wiremock::MockServer;
     use wiremock::Request;

+    use crate::ingestion::ingestion_client::CheckpointResult;
+    use crate::ingestion::ingestion_client::IngestionClientTrait;
     use crate::ingestion::store_client::tests::respond_with;
     use crate::ingestion::store_client::tests::respond_with_chain_id;
     use crate::ingestion::store_client::tests::status;
+    use crate::ingestion::streaming_client::test_utils::MockStreamingClient;
     use crate::ingestion::test_utils::test_checkpoint_data;
+    use crate::metrics::IngestionMetrics;
+    use crate::types::digests::ChainIdentifier;

     use super::*;

+    const FALLBACK: u64 = 99;
+
+    struct MockLatestCheckpoint(u64);
+
+    #[async_trait::async_trait]
+    impl IngestionClientTrait for MockLatestCheckpoint {
+        async fn chain_id(&self) -> anyhow::Result<ChainIdentifier> {
+            unimplemented!()
+        }
+        async fn checkpoint(&self, _: u64) -> CheckpointResult {
+            unimplemented!()
+        }
+        async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+            Ok(self.0)
+        }
+    }
+
+    fn mock_ingestion_client(latest_checkpoint: u64) -> IngestionClient {
+        let metrics = IngestionMetrics::new(None, &Registry::new());
+        IngestionClient::new_impl(Arc::new(MockLatestCheckpoint(latest_checkpoint)), metrics)
+    }
+
     async fn test_ingestion(
         uri: String,
         checkpoint_buffer_size: usize,
@@ -457,4 +547,48 @@ mod tests {
         let seqs = subscriber.await.unwrap();
         assert_eq!(seqs, vec![0, 1, 2, 3, 4, 5]);
     }
+
+    #[tokio::test]
+    async fn latest_checkpoint_number_no_streaming_client() {
+        let client = mock_ingestion_client(FALLBACK);
+        let mut streaming: Option<MockStreamingClient> = None;
+        let result = latest_checkpoint_number(&mut streaming, &client).await;
+        assert_eq!(result.unwrap(), FALLBACK);
+    }
+
+    #[tokio::test]
+    async fn latest_checkpoint_number_from_stream() {
+        let client = mock_ingestion_client(FALLBACK);
+        let mut streaming = Some(MockStreamingClient::new([42], None));
+        let result = latest_checkpoint_number(&mut streaming, &client).await;
+        assert_eq!(result.unwrap(), 42);
+    }
+
+    #[tokio::test]
+    async fn latest_checkpoint_number_stream_error_falls_back() {
+        let client = mock_ingestion_client(FALLBACK);
+        let mut mock = MockStreamingClient::new(std::iter::empty::<u64>(), None);
+        mock.insert_error();
+        let mut streaming = Some(mock);
+        let result = latest_checkpoint_number(&mut streaming, &client).await;
+        assert_eq!(result.unwrap(), FALLBACK);
+    }
+
+    #[tokio::test]
+    async fn latest_checkpoint_number_empty_stream_falls_back() {
+        let client = mock_ingestion_client(FALLBACK);
+        let mut streaming = Some(MockStreamingClient::new(std::iter::empty::<u64>(), None));
+        let result = latest_checkpoint_number(&mut streaming, &client).await;
+        assert_eq!(result.unwrap(), FALLBACK);
+    }
+
+    #[tokio::test]
+    async fn latest_checkpoint_number_connection_failure_falls_back() {
+        let client = mock_ingestion_client(FALLBACK);
+        let mut streaming = Some(
+            MockStreamingClient::new(std::iter::empty::<u64>(), None).fail_connection_times(1),
+        );
+        let result = latest_checkpoint_number(&mut streaming, &client).await;
+        assert_eq!(result.unwrap(), FALLBACK);
+    }
 }
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/rpc_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/rpc_client.rs
index 4b1634b70678d..d915c178168dc 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/rpc_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/rpc_client.rs
@@ -10,6 +10,7 @@ use sui_rpc::Client as RpcClient;
 use sui_rpc::field::FieldMaskUtil;
 use sui_rpc::proto::sui::rpc::v2::GetCheckpointRequest;
 use sui_rpc::proto::sui::rpc::v2::GetServiceInfoRequest;
+use sui_rpc::proto::sui::rpc::v2::GetServiceInfoResponse;
 use sui_types::digests::ChainIdentifier;
 use sui_types::digests::CheckpointDigest;
 use sui_types::full_checkpoint_content::Checkpoint;
@@ -23,13 +24,7 @@ use crate::ingestion::ingestion_client::IngestionClientTrait;
 #[async_trait]
 impl IngestionClientTrait for RpcClient {
     async fn chain_id(&self) -> anyhow::Result<ChainIdentifier> {
-        let request = GetServiceInfoRequest::const_default();
-        let response = self
-            .clone()
-            .ledger_client()
-            .get_service_info(request)
-            .await?
-            .into_inner();
+        let response = get_service_info_request(self).await?;
         Ok(CheckpointDigest::from_str(response.chain_id())?.into())
     }

@@ -63,4 +58,24 @@ impl IngestionClientTrait for RpcClient {
         Checkpoint::try_from(response.checkpoint())
             .map_err(|e| CheckpointError::Decode(ProtoConversion(e)))
     }
+
+    async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+        let response = get_service_info_request(self).await?;
+        let Some(latest_checkpoint_number) = response.checkpoint_height else {
+            return Err(anyhow!("Checkpoint height not found {response:?}"));
+        };
+        Ok(latest_checkpoint_number)
+    }
+}
+
+async fn get_service_info_request(
+    rpc_client: &RpcClient,
+) -> anyhow::Result<GetServiceInfoResponse> {
+    let request = GetServiceInfoRequest::const_default();
+    Ok(rpc_client
+        .clone()
+        .ledger_client()
+        .get_service_info(request)
+        .await?
+        .into_inner())
 }
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/store_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/store_client.rs
index 3791f9380aedf..e26aa4d430b0a 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/store_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/store_client.rs
@@ -3,6 +3,7 @@

 use std::sync::Arc;

+use anyhow::Context;
 use bytes::Bytes;
 use object_store::Error;
 use object_store::ObjectStore;
@@ -36,6 +37,14 @@ pub struct StoreIngestionClient {
     total_ingested_bytes: Option<IntCounter>,
 }

+// from sui-indexer-alt-object-store
+pub(crate) const WATERMARK_PATH: &str = "_metadata/watermark/checkpoint_blob.json";
+
+#[derive(serde::Deserialize, serde::Serialize)]
+pub(crate) struct ObjectStoreWatermark {
+    pub checkpoint_hi_inclusive: u64,
+}
+
 impl StoreIngestionClient {
     pub fn new(store: Arc<dyn ObjectStore>, total_ingested_bytes: Option<IntCounter>) -> Self {
         Self {
@@ -66,6 +75,17 @@ impl StoreIngestionClient {
         let result = self.store.get(&path).await?;
         result.bytes().await
     }
+
+    async fn watermark_checkpoint_hi_inclusive(&self) -> anyhow::Result<Option<u64>> {
+        let bytes = match self.bytes(ObjectPath::from(WATERMARK_PATH)).await {
+            Ok(bytes) => bytes,
+            Err(Error::NotFound { .. }) => return Ok(None),
+            Err(e) => return Err(e).context(format!("error reading {WATERMARK_PATH}")),
+        };
+        let watermark: ObjectStoreWatermark =
+            serde_json::from_slice(&bytes).context(format!("error parsing {WATERMARK_PATH}"))?;
+        Ok(Some(watermark.checkpoint_hi_inclusive))
+    }
 }

 #[async_trait::async_trait]
@@ -98,6 +118,12 @@ impl IngestionClientTrait for StoreIngestionClient {
         }
         decode::checkpoint(&bytes).map_err(CheckpointError::Decode)
     }
+
+    async fn latest_checkpoint_number(&self) -> anyhow::Result<u64> {
+        self.watermark_checkpoint_hi_inclusive()
+            .await
+            .map(|cp| cp.unwrap_or(0))
+    }
 }

 #[cfg(test)]
@@ -147,7 +173,7 @@ pub(crate) mod tests {
     /// `respond_with_chain_id` is mounted.
     pub(crate) fn expected_chain_id() -> ChainIdentifier {
         let bytes = test_checkpoint_data(0);
-        let checkpoint = crate::ingestion::decode::checkpoint(&bytes).unwrap();
+        let checkpoint = decode::checkpoint(&bytes).unwrap();
         (*checkpoint.summary.digest()).into()
     }

@@ -165,6 +191,56 @@ pub(crate) mod tests {
         IngestionClient::with_store(store, test_ingestion_metrics()).unwrap()
     }

+    async fn test_latest_checkpoint_number(watermark: ResponseTemplate) -> anyhow::Result<u64> {
+        let server = MockServer::start().await;
+
+        Mock::given(method("GET"))
+            .and(path(WATERMARK_PATH))
+            .respond_with(watermark)
+            .mount(&server)
+            .await;
+
+        let store = HttpBuilder::new()
+            .with_url(server.uri())
+            .with_client_options(ClientOptions::default().with_allow_http(true))
+            .build()
+            .map(Arc::new)
+            .unwrap();
+        let client = StoreIngestionClient::new(store, None);
+
+        IngestionClientTrait::latest_checkpoint_number(&client).await
+    }
+
+    #[tokio::test]
+    async fn test_latest_checkpoint_no_watermark() {
+        assert_eq!(
+            test_latest_checkpoint_number(status(StatusCode::NOT_FOUND))
+                .await
+                .unwrap(),
+            0
+        )
+    }
+
+    #[tokio::test]
+    async fn test_latest_checkpoint_corrupt_watermark() {
+        assert!(
+            test_latest_checkpoint_number(status(StatusCode::OK).set_body_string("<"))
+                .await
+                .is_err()
+        )
+    }
+
+    #[tokio::test]
+    async fn test_latest_checkpoint_from_watermark() {
+        let body = serde_json::json!({"checkpoint_hi_inclusive": 1}).to_string();
+        assert_eq!(
+            test_latest_checkpoint_number(status(StatusCode::OK).set_body_string(body))
+                .await
+                .unwrap(),
+            1
+        )
+    }
+
     #[tokio::test]
     async fn fail_on_not_found() {
         let server = MockServer::start().await;
@@ -276,7 +352,7 @@ pub(crate) mod tests {
             match times_clone.fetch_add(1, Ordering::Relaxed) {
                 0 => {
                     // Delay longer than our test timeout (2 seconds)
-                    std::thread::sleep(std::time::Duration::from_secs(4));
+                    std::thread::sleep(Duration::from_secs(4));
                     status(StatusCode::OK).set_body_bytes(test_checkpoint_data(42))
                 }
                 _ => {
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
index 4beafa7eb8643..b340da9caa0c7 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs
@@ -43,6 +43,7 @@ pub struct StreamingClientArgs {
 }

 /// gRPC-based implementation of the CheckpointStreamingClient trait.
+#[derive(Clone)]
 pub struct GrpcStreamingClient {
     uri: Uri;
     connection_timeout: Duration;
diff --git a/crates/sui-indexer-alt-framework/src/lib.rs b/crates/sui-indexer-alt-framework/src/lib.rs
index f3b3bf384bd97..4bf055c3d9efe 100644
--- a/crates/sui-indexer-alt-framework/src/lib.rs
+++ b/crates/sui-indexer-alt-framework/src/lib.rs
@@ -127,6 +127,9 @@ pub struct Indexer<S: Store> {
     /// this checkpoint.
     last_checkpoint: Option<u64>,

+    /// The network's latest checkpoint, when the indexer was started.
+    latest_checkpoint: u64,
+
     /// The minimum `next_checkpoint` across all pipelines. This is the checkpoint for the indexer
     /// to start ingesting from.
     next_checkpoint: u64,
@@ -220,12 +223,17 @@ impl<S: Store> Indexer<S> {
         let ingestion_service =
             IngestionService::new(client_args, ingestion_config, metrics_prefix, registry)?;

+        let latest_checkpoint = ingestion_service.latest_checkpoint_number().await?;
+
+        info!(latest_checkpoint, "Ingestion store state");
+
         Ok(Self {
             store,
             metrics,
             ingestion_service,
             first_checkpoint,
             last_checkpoint,
+            latest_checkpoint,
             next_checkpoint: u64::MAX,
             next_sequential_checkpoint: None,
             task: task.into_task(),
@@ -280,7 +288,7 @@ impl<S: Store> Indexer<S> {
     /// respective watermarks.
     ///
     /// Ingestion will stop after consuming the configured `last_checkpoint` if one is provided.
-    pub async fn run(self) -> anyhow::Result<Service> {
+    pub async fn run(self) -> Result<Service> {
         if let Some(enabled_pipelines) = self.enabled_pipelines {
             ensure!(
                 enabled_pipelines.is_empty(),
@@ -323,6 +331,7 @@ impl<S: Store> Indexer<S> {
     async fn add_pipeline<P: Processor + 'static>(
         &mut self,
         pipeline_task: String,
+        retention: Option<u64>,
     ) -> Result<Option<u64>> {
         ensure!(
             self.added_pipelines.insert(P::NAME),
@@ -339,7 +348,13 @@ impl<S: Store> Indexer<S> {

         // Create a new record based on `proposed_next_checkpoint` if one does not exist.
         // Otherwise, use the existing record and disregard the proposed value.
-        let proposed_next_checkpoint = self.first_checkpoint.unwrap_or(0);
+        let proposed_next_checkpoint = if let Some(first_checkpoint) = self.first_checkpoint {
+            first_checkpoint
+        } else if let Some(retention) = retention {
+            self.latest_checkpoint.saturating_sub(retention)
+        } else {
+            0
+        };
         let mut conn = self.store.connect().await?;
         let init_watermark = conn
             .init_watermark(&pipeline_task, proposed_next_checkpoint.checked_sub(1))
@@ -376,7 +391,8 @@ impl<S: ConcurrentStore> Indexer<S> {
     ) -> Result<()> {
         let pipeline_task =
             pipeline_task::<S>(H::NAME, self.task.as_ref().map(|t| t.task.as_str()))?;
-        let Some(next_checkpoint) = self.add_pipeline::<H>(pipeline_task).await? else {
+        let retention = config.pruner.as_ref().map(|p| p.retention);
+        let Some(next_checkpoint) = self.add_pipeline::<H>(pipeline_task, retention).await? else {
             return Ok(());
         };

@@ -418,7 +434,7 @@ impl<T: SequentialStore> Indexer<T> {
             );
         }

-        let Some(next_checkpoint) = self.add_pipeline::<H>(H::NAME.to_owned()).await? else {
+        let Some(next_checkpoint) = self.add_pipeline::<H>(H::NAME.to_owned(), None).await? else {
             return Ok(());
         };

@@ -457,6 +473,8 @@ mod tests {
     use crate::config::ConcurrencyConfig;
     use crate::ingestion::ingestion_client::IngestionClientArgs;
+    use crate::ingestion::store_client::ObjectStoreWatermark;
+    use crate::ingestion::store_client::WATERMARK_PATH;
     use crate::mocks::store::MockStore;
     use crate::pipeline::CommitterConfig;
     use crate::pipeline::Processor;
@@ -492,7 +510,7 @@ mod tests {
         async fn process(
             &self,
             checkpoint: &Arc<sui_types::full_checkpoint_content::Checkpoint>,
-        ) -> anyhow::Result<Vec<Self::Value>> {
+        ) -> Result<Vec<Self::Value>> {
             let cp_num = checkpoint.summary.sequence_number;

             // Wait until the checkpoint is allowed to be processed
@@ -524,7 +542,7 @@ mod tests {
             &self,
             batch: &Self::Batch,
             conn: &mut <Self::Store as Store>::Connection<'a>,
-        ) -> anyhow::Result<usize> {
+        ) -> Result<usize> {
             for value in batch {
                 conn.0
                     .commit_data(Self::NAME, value.0, vec![value.0])
@@ -545,7 +563,7 @@ mod tests {
                 async fn process(
                     &self,
                     checkpoint: &Arc<sui_types::full_checkpoint_content::Checkpoint>,
-                ) -> anyhow::Result<Vec<Self::Value>> {
+                ) -> Result<Vec<Self::Value>> {
                     Ok(vec![MockValue(checkpoint.summary.sequence_number)])
                 }
             }
@@ -568,7 +586,7 @@ mod tests {
                     &self,
                     batch: &Self::Batch,
                     conn: &mut <Self::Store as Store>::Connection<'a>,
-                ) -> anyhow::Result<usize> {
+                ) -> Result<usize> {
                     for value in batch {
                         conn.0
                             .commit_data(Self::NAME, value.0, vec![value.0])
@@ -591,7 +609,7 @@ mod tests {
                     &self,
                     _batch: &Self::Batch,
                     _conn: &mut <Self::Store as Store>::Connection<'a>,
-                ) -> anyhow::Result<usize> {
+                ) -> Result<usize> {
                     Ok(1)
                 }
             }
@@ -602,6 +620,19 @@ mod tests {
     test_pipeline!(SequentialHandler, "sequential_handler");
     test_pipeline!(MockCheckpointSequenceNumberHandler, "test");

+    fn init_ingestion_dir(latest_checkpoint: Option<u64>) -> tempfile::TempDir {
+        let dir = tempfile::tempdir().unwrap();
+        if let Some(cp) = latest_checkpoint {
+            let watermark_path = dir.path().join(WATERMARK_PATH);
+            std::fs::create_dir_all(watermark_path.parent().unwrap()).unwrap();
+            let watermark = ObjectStoreWatermark {
+                checkpoint_hi_inclusive: cp,
+            };
+            std::fs::write(watermark_path, serde_json::to_string(&watermark).unwrap()).unwrap();
+        }
+        dir
+    }
+
     /// If `ingestion_data` is `Some((num_checkpoints, checkpoint_size))`, synthetic ingestion
     /// data will be generated in the temp directory before creating the indexer.
     async fn create_test_indexer(
@@ -610,7 +641,7 @@ mod tests {
         registry: &Registry,
         ingestion_data: Option<(u64, u64)>,
     ) -> (Indexer<MockStore>, tempfile::TempDir) {
-        let temp_dir = tempfile::tempdir().unwrap();
+        let temp_dir = init_ingestion_dir(None);
         if let Some((num_checkpoints, checkpoint_size)) = ingestion_data {
             synthetic_ingestion::generate_ingestion(synthetic_ingestion::Config {
                 ingestion_dir: temp_dir.path().to_owned(),
@@ -721,6 +752,76 @@ mod tests {
         )
     }

+    const LATEST_CHECKPOINT: u64 = 10;
+
+    /// Set up an indexer as if the network is at `latest_checkpoint` (the next checkpoint to
+    /// ingest). Runs a single concurrent pipeline with the given config. If `watermark` is
+    /// provided, the pipeline's high watermark is pre-set; `first_checkpoint` controls where
+    /// ingestion begins.
+    async fn test_next_checkpoint(
+        watermark: Option<u64>,
+        first_checkpoint: Option<u64>,
+        concurrent_config: ConcurrentConfig,
+    ) -> Indexer<MockStore> {
+        let registry = Registry::new();
+        let store = MockStore::default();
+
+        test_pipeline!(A, "concurrent_a");
+
+        if let Some(checkpoint_hi_inclusive) = watermark {
+            let mut conn = store.connect().await.unwrap();
+            conn.set_committer_watermark(
+                A::NAME,
+                CommitterWatermark {
+                    checkpoint_hi_inclusive,
+                    ..Default::default()
+                },
+            )
+            .await
+            .unwrap();
+        }
+
+        let temp_dir = init_ingestion_dir(Some(LATEST_CHECKPOINT));
+        let mut indexer = Indexer::new(
+            store,
+            IndexerArgs {
+                first_checkpoint,
+                ..Default::default()
+            },
+            ClientArgs {
+                ingestion: IngestionClientArgs {
+                    local_ingestion_path: Some(temp_dir.path().to_owned()),
+                    ..Default::default()
+                },
+                ..Default::default()
+            },
+            IngestionConfig::default(),
+            None,
+            &registry,
+        )
+        .await
+        .unwrap();
+
+        assert_eq!(indexer.latest_checkpoint, LATEST_CHECKPOINT);
+
+        indexer
+            .concurrent_pipeline::<A>(A, concurrent_config)
+            .await
+            .unwrap();
+
+        indexer
+    }
+
+    fn pruner_config(retention: u64) -> ConcurrentConfig {
+        ConcurrentConfig {
+            pruner: Some(concurrent::PrunerConfig {
+                retention,
+                ..Default::default()
+            }),
+            ..Default::default()
+        }
+    }
+
     #[test]
     fn test_arg_parsing() {
         #[derive(Parser)
@@ -788,6 +889,7 @@ mod tests {

         assert_eq!(indexer.first_checkpoint, None);
         assert_eq!(indexer.last_checkpoint, None);
+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexer.next_checkpoint, 2);
         assert_eq!(indexer.next_sequential_checkpoint, Some(2));
     }
@@ -817,6 +919,7 @@ mod tests {

         assert_eq!(indexer.first_checkpoint, None);
         assert_eq!(indexer.last_checkpoint, None);
+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexer.next_checkpoint, 0);
         assert_eq!(indexer.next_sequential_checkpoint, Some(0));
     }
@@ -879,6 +982,7 @@ mod tests {

         assert_eq!(indexer.first_checkpoint, Some(5));
         assert_eq!(indexer.last_checkpoint, None);
+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexer.next_checkpoint, 5);
         assert_eq!(indexer.next_sequential_checkpoint, Some(5));
     }
@@ -909,6 +1013,7 @@ mod tests {

         assert_eq!(indexer.first_checkpoint, Some(5));
         assert_eq!(indexer.last_checkpoint, None);
+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexe+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexer.next_checkpoint, 11);
         assert_eq!(indexer.next_sequential_checkpoint, Some(11));
     }
@@ -942,10 +1047,78 @@ mod tests {

         assert_eq!(indexer.first_checkpoint, Some(24));
         assert_eq!(indexer.last_checkpoint, None);
+        assert_eq!(indexer.latest_checkpoint, 0);
         assert_eq!(indexer.next_checkpoint, 11);
         assert_eq!(indexer.next_sequential_checkpoint, Some(11));
     }

+    /// latest_checkpoint is read from the watermark file.
+    #[tokio::test]
+    async fn test_latest_checkpoint_from_watermark() {
+        let registry = Registry::new();
+        let store = MockStore::default();
+        let temp_dir = init_ingestion_dir(Some(30));
+        let indexer = Indexer::new(
+            store,
+            IndexerArgs::default(),
+            ClientArgs {
+                ingestion: IngestionClientArgs {
+                    local_ingestion_path: Some(temp_dir.path().to_owned()),
+                    ..Default::default()
+                },
+                ..Default::default()
+            },
+            IngestionConfig::default(),
+            None,
+            &registry,
+        )
+        .await
+        .unwrap();
+
+        assert_eq!(indexer.latest_checkpoint, 30);
+    }
+
+    /// No watermark, no first_checkpoint, pruner with retention:
+    /// next_checkpoint = LATEST_CHECKPOINT - retention.
+    #[tokio::test]
+    async fn test_next_checkpoint_with_pruner_uses_retention() {
+        let retention = LATEST_CHECKPOINT - 1;
+        let indexer = test_next_checkpoint(None, None, pruner_config(retention)).await;
+        assert_eq!(indexer.next_checkpoint, LATEST_CHECKPOINT - retention);
+    }
+
+    /// No watermark, no first_checkpoint, no pruner: falls back to 0.
+    #[tokio::test]
+    async fn test_next_checkpoint_without_pruner_falls_back_to_genesis() {
+        let indexer = test_next_checkpoint(None, None, ConcurrentConfig::default()).await;
+        assert_eq!(indexer.next_checkpoint, 0);
+    }
+
+    /// Watermark at 5 takes priority over latest_checkpoint - retention.
+    #[tokio::test]
+    async fn test_next_checkpoint_watermark_takes_priority_over_pruner() {
+        let retention = LATEST_CHECKPOINT - 1;
+        let indexer = test_next_checkpoint(Some(5), None, pruner_config(retention)).await;
+        assert_eq!(indexer.next_checkpoint, 6);
+    }
+
+    /// first_checkpoint takes priority over latest_checkpoint - retention when
+    /// there's no watermark.
+    #[tokio::test]
+    async fn test_next_checkpoint_first_checkpoint_takes_priority_over_pruner() {
+        let retention = LATEST_CHECKPOINT - 1;
+        let indexer = test_next_checkpoint(None, Some(2), pruner_config(retention)).await;
+        assert_eq!(indexer.next_checkpoint, 2);
+    }
+
+    /// When retention exceeds latest_checkpoint, saturating_sub clamps to 0.
+    #[tokio::test]
+    async fn test_next_checkpoint_retention_exceeds_latest_checkpoint() {
+        let retention = LATEST_CHECKPOINT + 1;
+        let indexer = test_next_checkpoint(None, None, pruner_config(retention)).await;
+        assert_eq!(indexer.next_checkpoint, 0);
+    }
+
     // test ingestion, all pipelines have watermarks, no first_checkpoint provided
     #[tokio::test]
     async fn test_indexer_ingestion_existing_watermarks_no_first_checkpoint() {
@@ -987,6 +1160,47 @@ mod tests {
         assert_out_of_order!(indexer_metrics, D::NAME, 15);
     }

+    // test ingestion, no pipelines missing watermarks, first_checkpoint provided
+    #[tokio::test]
+    async fn test_indexer_ingestion_existing_watermarks_ignore_first_checkpoint() {
+        let registry = Registry::new();
+        let store = MockStore::default();
+
+        test_pipeline!(A, "concurrent_a");
+        test_pipeline!(B, "concurrent_b");
+        test_pipeline!(C, "sequential_c");
+        test_pipeline!(D, "sequential_d");
+
+        let mut conn = store.connect().await.unwrap();
+        set_committer_watermark(&mut conn, A::NAME, 5).await;
+        let mut conn = store.connect().await.unwrap();
+        set_committer_watermark(&mut conn, B::NAME, 10).await;
+        let mut conn = store.connect().await.unwrap();
+        set_committer_watermark(&mut conn, C::NAME, 15).await;
+        let mut conn = store.connect().await.unwrap();
+        set_committer_watermark(&mut conn, D::NAME, 20).await;
+
+        let indexer_args = IndexerArgs {
+            first_checkpoint: Some(3),
+            last_checkpoint: Some(29),
+            ..Default::default()
+        };
+        let (mut indexer, _temp_dir) =
+            create_test_indexer(store.clone(), indexer_args, &registry, Some((30, 1))).await;
+
+        add_concurrent(&mut indexer, A).await;
+        add_concurrent(&mut indexer, B).await;
+        add_sequential(&mut indexer, C).await;
+        add_sequential(&mut indexer, D).await;
+
+        let ingestion_metrics = indexer.ingestion_metrics().clone();
+        let metrics = indexer.indexer_metrics().clone();
+        indexer.run().await.unwrap().join().await.unwrap();
+
+        assert_eq!(ingestion_metrics.total_ingested_checkpoints.get(), 24);
+        assert_out_of_order!(metrics, A::NAME, 0);
+        assert_out_of_order!(metrics, B::NAME, 5);
+        assert_out_of_order!(metrics, C::NAME, 10);
+        assert_out_of_order!(metrics, D::NAME, 15);
+    }
+
     // test ingestion, all pipelines have watermarks, first_checkpoint provided
     #[tokio::test]
     async fn test_indexer_ingestion_existing_watermarks_first_checkpoint_ignored() {
diff --git a/crates/sui-indexer-alt-framework/src/metrics.rs b/crates/sui-indexer-alt-framework/src/metrics.rs
index 616d3af25735c..5373f920cc269 100644
--- a/crates/sui-indexer-alt-framework/src/metrics.rs
+++ b/crates/sui-indexer-alt-framework/src/metrics.rs
@@ -78,6 +78,7 @@ pub struct IngestionMetrics {

     pub ingested_checkpoint_latency: Histogram,
     pub ingested_chain_id_latency: Histogram,
+    pub ingested_latest_checkpoint_latency: Histogram,

     pub ingestion_concurrency_limit: IntGauge,
     pub ingestion_concurrency_inflight: IntGauge,
@@ -301,6 +302,13 @@ impl IngestionMetrics {
                 registry,
             )
             .unwrap(),
+            ingested_latest_checkpoint_latency: register_histogram_with_registry!(
+                name("ingested_latest_checkpoint_latency"),
+                "Time taken to fetch the latest checkpoint number, including retries",
+                INGESTION_LATENCY_SEC_BUCKETS.to_vec(),
+                registry,
+            )
+            .unwrap(),
             ingestion_concurrency_limit: register_int_gauge_with_registry!(
                 name("ingestion_concurrency_limit"),
                 "Current adaptive concurrency limit for checkpoint ingestion",

diff --git a/crates/sui-indexer-alt-framework/src/pipeline/concurrent/mod.rs b/crates/sui-indexer-alt-framework/src/pipeline/concurrent/mod.rs
index 4d9890f5669d6..0cf706031b857 100644
--- a/crates/sui-indexer-alt-framework/src/pipeline/concurrent/mod.rs
+++ b/crates/sui-indexer-alt-framework/src/pipeline/concurrent/mod.rs
@@ -554,22 +554,32 @@ mod tests {
             assert_eq!(data, vec![i * 10 + 1, i * 10 + 2]);
         }

-        // Wait for pruning to occur (5s + delay + processing time)
-        tokio::time::sleep(Duration::from_millis(5_200)).await;
+        // Wait for pruning to occur. The pruner and reader_watermark tasks both run on
+        // the same interval, so poll until the pruner has caught up rather instead of using a
+        // fixed sleep.
+        let pruning_deadline = Duration::from_secs(15);
+        let start = tokio::time::Instant::now();
+        loop {
+            let pruned = {
+                let data = setup.store.data.get(DataPipeline::NAME).unwrap();
+                !data.contains_key(&0) && !data.contains_key(&1) && !data.contains_key(&2)
+            };
+            if pruned {
+                break;
+            }
+            assert!(
+                start.elapsed() < pruning_deadline,
+                "Timed out waiting for pruning to occur"
+            );
+            tokio::time::sleep(Duration::from_millis(100)).await;
+        }

-        // Verify pruning has occurred
+        // Verify recent checkpoints are still available
         {
             let data = setup.store.data.get(DataPipeline::NAME).unwrap();
-
-            // Verify recent checkpoints are still available
             assert!(data.contains_key(&3));
             assert!(data.contains_key(&4));
             assert!(data.contains_key(&5));
-
-            // Verify old checkpoints are pruned
-            assert!(!data.contains_key(&0));
-            assert!(!data.contains_key(&1));
-            assert!(!data.contains_key(&2));
         };
     }

PATCH

# Idempotency check - verify the distinctive line exists
grep -q "latest_checkpoint_number" /workspace/sui/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs && echo "Patch already applied - exiting" && exit 0

echo "Patch applied successfully"
