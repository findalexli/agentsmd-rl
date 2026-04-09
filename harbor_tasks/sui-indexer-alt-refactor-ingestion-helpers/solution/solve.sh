#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "async fn retry_transient_with_slow_monitor" crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs b/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
index 919dd334996c..0626290df6b8 100644
--- a/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
+++ b/crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs
@@ -1,6 +1,7 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0

+use std::future::Future;
 use std::path::PathBuf;
 use std::sync::Arc;
 use std::time::Duration;
@@ -18,6 +19,7 @@ use object_store::azure::MicrosoftAzureBuilder;
 use object_store::gcp::GoogleCloudStorageBuilder;
 use object_store::http::HttpBuilder;
 use object_store::local::LocalFileSystem;
+use prometheus::Histogram;
 use sui_futures::future::with_slow_future_monitor;
 use sui_rpc::Client;
 use sui_rpc::client::HeadersInterceptor;
@@ -28,11 +30,10 @@ use tracing::error;
 use tracing::warn;
 use url::Url;

-use crate::ingestion::Error as IngestionError;
+use crate::ingestion::Error as IE;
 use crate::ingestion::MAX_GRPC_MESSAGE_SIZE_BYTES;
 use crate::ingestion::Result as IngestionResult;
 use crate::ingestion::decode;
-use crate::ingestion::error::Error::FetchError;
 use crate::ingestion::store_client::StoreIngestionClient;
 use crate::metrics::CheckpointLagMetricReporter;
 use crate::metrics::IngestionMetrics;
@@ -300,7 +301,7 @@ impl IngestionClient {
         let fetch = || async move {
             use backoff::Error as BE;
             self.checkpoint(checkpoint).await.map_err(|e| match e {
-                IngestionError::NotFound(checkpoint) => {
+                IE::NotFound(checkpoint) => {
                     debug!(checkpoint, "Checkpoint not found, retrying...");
                     self.metrics.total_ingested_not_found_retries.inc();
                     BE::transient(e)
@@ -320,92 +321,90 @@ impl IngestionClient {
     /// this function if we fail to deserialize the result as [Checkpoint].
     ///
     /// The function will immediately return if the checkpoint is not found.
-    pub async fn checkpoint(&self, checkpoint: u64) -> IngestionResult<CheckpointEnvelope> {
-        let checkpoint_client = self.client.clone();
-        let request = move || {
-            let client = checkpoint_client.clone();
-            async move {
-                let checkpoint_data = with_slow_future_monitor(
-                    client.checkpoint(checkpoint),
-                    SLOW_OPERATION_WARNING_THRESHOLD,
-                    /* on_threshold_exceeded =*/
-                    || {
-                        warn!(
-                            checkpoint,
-                            threshold_ms = SLOW_OPERATION_WARNING_THRESHOLD.as_millis(),
-                            "Slow checkpoint operation detected"
-                        );
-                    },
-                )
-                .await
-                .map_err(|err| match err {
-                    CheckpointError::NotFound => {
-                        BE::permanent(IngestionError::NotFound(checkpoint))
-                    }
-                    CheckpointError::Transient { reason, error } => self.metrics.inc_retry(
-                        checkpoint,
-                        reason,
-                        IngestionError::FetchError(checkpoint, error),
-                    ),
-                    CheckpointError::Permanent { reason, error } => {
-                        error!(checkpoint, reason, "Permanent checkpoint error: {error}");
-                        self.metrics
-                            .total_ingested_permanent_errors
-                            .with_label_values(&[reason])
-                            .inc();
-                        BE::permanent(IngestionError::FetchError(checkpoint, error))
-                    }
-                })?;
-
-                Ok::<Checkpoint, backoff::Error<IngestionError>>(match checkpoint_data {
-                    CheckpointData::Raw(bytes) => {
-                        self.metrics.total_ingested_bytes.inc_by(bytes.len() as u64);
-
-                        decode::checkpoint(&bytes).map_err(|e| {
-                            self.metrics.inc_retry(
-                                checkpoint,
-                                e.reason(),
-                                IngestionError::DeserializationError(checkpoint, e.into()),
-                            )
-                        })?
-                    }
-                    CheckpointData::Checkpoint(data) => {
-                        // We are not recording size metric for Checkpoint data (from RPC client).
-                        // TODO: Record the metric when we have a good way to get the size information
-                        data
+    pub async fn checkpoint(&self, cp_sequence_number: u64) -> IngestionResult<CheckpointEnvelope> {
+        let client = self.client.clone();
+        let checkpoint_data_fut =
+            retry_transient_with_slow_monitor(
+                "checkpoint",
+                move || {
+                    let client = client.clone();
+                    async move {
+                        let checkpoint_data = client.checkpoint(cp_sequence_number).await.map_err(
+                            |err| match err {
+                                CheckpointError::NotFound => {
+                                    BE::permanent(IE::NotFound(cp_sequence_number))
+                                }
+                                CheckpointError::Transient { reason, error } => {
+                                    self.metrics.inc_retry(
+                                        cp_sequence_number,
+                                        reason,
+                                        IE::FetchError(cp_sequence_number, error),
+                                    )
+                                }
+                                CheckpointError::Permanent { reason, error } => {
+                                    error!(
+                                        cp_sequence_number,
+                                        reason, "Permanent checkpoint error: {error}"
+                                    );
+                                    self.metrics
+                                        .total_ingested_permanent_errors
+                                        .with_label_values(&[reason])
+                                        .inc();
+                                    BE::permanent(IE::FetchError(cp_sequence_number, error))
+                                }
+                            },
+                        )?;
+
+                        Ok::<Checkpoint, backoff::Error<IE>>(match checkpoint_data {
+                            CheckpointData::Raw(bytes) => {
+                                self.metrics.total_ingested_bytes.inc_by(bytes.len() as u64);
+
+                                decode::checkpoint(&bytes).map_err(|e| {
+                                    self.metrics.inc_retry(
+                                        cp_sequence_number,
+                                        e.reason(),
+                                        IE::DeserializationError(cp_sequence_number, e.into()),
+                                    )
+                                })?
+                            }
+                            CheckpointData::Checkpoint(data) => data,
+                        })
                     }
-                })
-            }
-        };
-
-        // Keep backing off until we are waiting for the max interval, but don't give up.
-        let backoff = ExponentialBackoff {
-            max_interval: MAX_TRANSIENT_RETRY_INTERVAL,
-            max_elapsed_time: None,
-            ..Default::default()
-        };
+                },
+                &self.metrics.ingested_checkpoint_latency,
+            );

-        let guard = self.metrics.ingested_checkpoint_latency.start_timer();
-        let data = backoff::future::retry(backoff, request).await?;
-        let elapsed = guard.stop_and_record();
+        let client = self.client.clone();
+        let chain_id_fut = self.chain_id.get_or_try_init(|| {
+            retry_transient_with_slow_monitor(
+                "chain_id",
+                move || {
+                    let client = client.clone();
+                    async move {
+                        client
+                            .chain_id()
+                            .await
+                            .map_err(|e| BE::transient(IE::FetchError(cp_sequence_number, e)))
+                    }
+                },
+                &self.metrics.ingested_chain_id_latency,
+            )
+        });

-        debug!(
-            checkpoint,
-            elapsed_ms = elapsed * 1000.0,
-            "Fetched checkpoint"
-        );
+        let (checkpoint, chain_id) = tokio::try_join!(checkpoint_data_fut, chain_id_fut)?;

         self.checkpoint_lag_reporter
-            .report_lag(checkpoint, data.summary.timestamp_ms);
+            .report_lag(cp_sequence_number, checkpoint.summary.timestamp_ms);

         self.metrics.total_ingested_checkpoints.inc();

         self.metrics
             .total_ingested_transactions
-            .inc_by(data.transactions.len() as u64);
+            .inc_by(checkpoint.transactions.len() as u64);

         self.metrics.total_ingested_events.inc_by(
-            data.transactions
+            checkpoint
+                .transactions
                 .iter()
                 .map(|tx| tx.events.as_ref().map_or(0, |evs| evs.data.len()) as u64)
                 .sum(),
@@ -413,69 +412,71 @@ impl IngestionClient {

         self.metrics
             .total_ingested_objects
-            .inc_by(data.object_set.len() as u64);
-
-        let chain_id = *self.get_or_init_chain_id(checkpoint).await?;
+            .inc_by(checkpoint.object_set.len() as u64);

         Ok(CheckpointEnvelope {
-            checkpoint: Arc::new(data),
-            chain_id,
+            checkpoint: Arc::new(checkpoint),
+            chain_id: *chain_id,
         })
     }
+}

-    async fn get_or_init_chain_id(&self, checkpoint: u64) -> IngestionResult<&ChainIdentifier> {
-        let chain_id_client = self.client.clone();
-        let chain_id = self
-            .chain_id
-            .get_or_try_init(|| {
-                let request = move || {
-                    let client = chain_id_client.clone();
-                    async move {
-                        let chain_id = with_slow_future_monitor(
-                            client.chain_id(),
-                            SLOW_OPERATION_WARNING_THRESHOLD,
-                            /* on_threshold_exceeded =*/
-                            || {
-                                warn!(
-                                    checkpoint,
-                                    threshold_ms = SLOW_OPERATION_WARNING_THRESHOLD.as_millis(),
-                                    "Slow chain_id operation detected"
-                                );
-                            },
-                        )
-                        .await
-                        .map_err(|err| {
-                            let reason = "chain_id";
-                            warn!(reason, "Retrying due to error: {err}");
-                            backoff::Error::transient(FetchError(checkpoint, err))
-                        })?;
-
-                        Ok::<ChainIdentifier, backoff::Error<IngestionError>>(chain_id)
-                    }
-                };
-
-                // Keep backing off until we are waiting for the max interval, but don't give up.
-                let backoff = ExponentialBackoff {
-                    max_interval: MAX_TRANSIENT_RETRY_INTERVAL,
-                    max_elapsed_time: None,
-                    ..Default::default()
-                };
+/// Keep backing off until we are waiting for the max interval, but don't give up.
+fn transient_backoff() -> ExponentialBackoff {
+    ExponentialBackoff {
+        max_interval: MAX_TRANSIENT_RETRY_INTERVAL,
+        max_elapsed_time: None,
+        ..Default::default()
+    }
+}

-                backoff::future::retry(backoff, request)
+/// Retry a fallible async operation with exponential backoff and slow-operation monitoring.
+/// Records the total time (including retries) in the provided latency histogram.
+async fn retry_transient_with_slow_monitor<F, Fut, T>(
+    operation: &str,
+    make_future: F,
+    latency: &Histogram,
+) -> IngestionResult<T>
+where
+    F: Fn() -> Fut,
+    Fut: Future<Output = Result<T, backoff::Error<IE>>>,
+{
+    let request = || {
+        let fut = make_future();
+        async move {
+            with_slow_future_monitor(fut, SLOW_OPERATION_WARNING_THRESHOLD, || {
+                warn!(
+                    operation,
+                    threshold_ms = SLOW_OPERATION_WARNING_THRESHOLD.as_millis(),
+                    "Slow operation detected"
+                );
             })
-            .await?;
-        Ok(chain_id)
-    }
+            .await
+        }
+    };
+
+    let guard = latency.start_timer();
+    let data = backoff::future::retry(transient_backoff(), request).await?;
+    let elapsed = guard.stop_and_record();
+
+    debug!(
+        operation,
+        elapsed_ms = elapsed * 1000.0,
+        "Fetched operation"
+    );
+
+    Ok(data)
 }

 #[cfg(test)]
 mod tests {
+    use std::sync::Arc;
+    use std::time::Duration;
+
     use clap::Parser;
     use clap::error::ErrorKind;
     use dashmap::DashMap;
     use prometheus::Registry;
-    use std::sync::Arc;
-    use std::time::Duration;
     use sui_types::digests::CheckpointDigest;
     use tokio::time::timeout;

@@ -642,7 +643,7 @@ mod tests {

         // Try to fetch non-existent checkpoint
         let result = client.checkpoint(1).await;
-        assert!(matches!(result, Err(IngestionError::NotFound(1))));
+        assert!(matches!(result, Err(IE::NotFound(1))));
     }

     #[tokio::test]
@@ -731,7 +732,7 @@ mod tests {
         mock.permanent_failures.insert(1, 1);

         let result = client.checkpoint(1).await;
-        assert!(matches!(result, Err(IngestionError::FetchError(1, _))));
+        assert!(matches!(result, Err(IE::FetchError(1, _))));

         // Verify that the non-retryable error metric was incremented
         let errors = client
@@ -740,3 +741,4 @@ mod tests {
         assert!(errors > 0);
     }
 }
+
diff --git a/crates/sui-indexer-alt-framework/src/metrics.rs b/crates/sui-indexer-alt-framework/src/metrics.rs
index 9dfb5854e066..3fb5bba5568c 100644
--- a/crates/sui-indexer-alt-framework/src/metrics.rs
+++ b/crates/sui-indexer-alt-framework/src/metrics.rs
@@ -78,6 +78,7 @@ pub struct IngestionMetrics {
     pub ingested_checkpoint_timestamp_lag: Histogram,

     pub ingested_checkpoint_latency: Histogram,
+    pub ingested_chain_id_latency: Histogram,

     pub ingestion_concurrency_limit: IntGauge,
     pub ingestion_concurrency_inflight: IntGauge,
@@ -303,6 +304,13 @@ impl IngestionMetrics {
                 registry,
             )
             .unwrap(),
+            ingested_chain_id_latency: register_histogram_with_registry!(
+                name("ingested_chain_id_latency"),
+                "Time taken to fetch the chain identifier, including retries",
+                INGESTION_LATENCY_SEC_BUCKETS.to_vec(),
+                registry,
+            )
+            .unwrap(),
             ingestion_concurrency_limit: register_int_gauge_with_registry!(
                 name("ingestion_concurrency_limit"),
                 "Current adaptive concurrency limit for checkpoint ingestion",
PATCH

echo "Patch applied successfully"
