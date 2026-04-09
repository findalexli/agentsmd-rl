#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched (idempotency)
if grep -q "try_join_all" crates/sui-indexer-alt-reader/src/checkpoints.rs; then
    echo "Already patched, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/crates/sui-indexer-alt-reader/src/checkpoints.rs b/crates/sui-indexer-alt-reader/src/checkpoints.rs
index bfc91979df599..32ab48b3faaf2 100644
--- a/crates/sui-indexer-alt-reader/src/checkpoints.rs
+++ b/crates/sui-indexer-alt-reader/src/checkpoints.rs
@@ -8,6 +8,7 @@ use anyhow::Context;
 use async_graphql::dataloader::Loader;
 use diesel::ExpressionMethods;
 use diesel::QueryDsl;
+use futures::future::try_join_all;
 use prost_types::FieldMask;
 use sui_indexer_alt_schema::checkpoints::StoredCheckpoint;
 use sui_indexer_alt_schema::schema::kv_checkpoints;
@@ -105,8 +106,7 @@ impl Loader<CheckpointKey> for LedgerGrpcReader {
             return Ok(HashMap::new());
         }

-        let mut results = HashMap::new();
-        for key in keys {
+        let futures = keys.iter().map(|key| async {
             let request = proto::GetCheckpointRequest::by_sequence_number(key.0).with_read_mask(
                 FieldMask::from_paths(["summary.bcs", "signature", "contents.bcs"]),
             );
@@ -139,12 +139,14 @@ impl Loader<CheckpointKey> for LedgerGrpcReader {
                         AuthorityQuorumSignInfo::from(sdk_sig)
                     };

-                    results.insert(*key, (summary, contents, signature));
+                    Ok(Some((*key, (summary, contents, signature))))
                 }
-                Err(status) if status.code() == tonic::Code::NotFound => continue,
-                Err(e) => return Err(e.into()),
+                Err(status) if status.code() == tonic::Code::NotFound => Ok(None),
+                Err(e) => Err(Error::from(e)),
             }
-        }
-        Ok(results)
+        });
+
+        let results: Vec<_> = try_join_all(futures).await?;
+        Ok(results.into_iter().flatten().collect())
     }
 }
diff --git a/crates/sui-indexer-alt-reader/src/events.rs b/crates/sui-indexer-alt-reader/src/events.rs
index f5519030e167c..e734df27ec7c3 100644
--- a/crates/sui-indexer-alt-reader/src/events.rs
+++ b/crates/sui-indexer-alt-reader/src/events.rs
@@ -114,47 +114,60 @@ impl Loader<TransactionEventsKey> for LedgerGrpcReader {
             return Ok(HashMap::new());
         }

-        let mut results = HashMap::new();
-        for key in keys {
-            let request = proto::GetTransactionRequest::new(&key.0.into())
-                .with_read_mask(FieldMask::from_paths(["events.bcs", "timestamp"]));
-
-            match self.get_transaction(request).await {
-                Ok(response) => {
-                    let executed = response.transaction.context("No transaction returned")?;
-
-                    let events = executed
-                        .events
-                        .as_ref()
-                        .and_then(|e| e.bcs.as_ref())
-                        .map(|bcs| -> anyhow::Result<_> {
-                            let tx_events: TransactionEvents = bcs
-                                .deserialize()
-                                .context("Failed to deserialize transaction events")?;
-                            Ok(tx_events.data)
-                        })
-                        .transpose()?
-                        .unwrap_or_default();
-
-                    let timestamp_ms = executed
-                        .timestamp
-                        .map(proto_to_timestamp_ms)
-                        .transpose()
-                        .map_err(|e| anyhow!("Failed to parse timestamp: {}", e))?
-                        .unwrap_or(0);
-
-                    results.insert(
-                        *key,
-                        TransactionEventsData {
-                            events,
-                            timestamp_ms,
-                        },
-                    );
+        let digests = keys.iter().map(|key| key.0.to_string()).collect();
+
+        let mut request = proto::BatchGetTransactionsRequest::default();
+        request.digests = digests;
+        request.read_mask = Some(FieldMask::from_paths(["digest", "events.bcs", "timestamp"]));
+
+        let batch_response = self.batch_get_transactions(request).await?;
+
+        batch_response
+            .transactions
+            .into_iter()
+            .filter_map(|tx_result| match tx_result.result {
+                Some(proto::get_transaction_result::Result::Transaction(executed)) => {
+                    Some(executed)
                 }
-                Err(status) if status.code() == tonic::Code::NotFound => continue,
-                Err(e) => return Err(e.into()),
-            }
-        }
-        Ok(results)
+                _ => None,
+            })
+            .map(|executed| {
+                let digest: TransactionDigest = executed
+                    .digest
+                    .as_ref()
+                    .context("Missing transaction digest")?
+                    .parse()
+                    .context("Failed to parse transaction digest")?;
+
+                let events = executed
+                    .events
+                    .as_ref()
+                    .and_then(|e| e.bcs.as_ref())
+                    .map(|bcs| -> anyhow::Result<_> {
+                        let tx_events: TransactionEvents = bcs
+                            .deserialize()
+                            .context("Failed to deserialize transaction events")?;
+                        Ok(tx_events.data)
+                    })
+                    .transpose()?
+                    .unwrap_or_default();
+
+                let timestamp_ms = executed
+                    .timestamp
+                    .map(proto_to_timestamp_ms)
+                    .transpose()
+                    .map_err(|e| anyhow!("Failed to parse timestamp: {}", e))?
+                    .unwrap_or(0);
+
+                Ok((
+                    TransactionEventsKey(digest),
+                    TransactionEventsData {
+                        events,
+                        timestamp_ms,
+                    },
+                ))
+            })
+            .collect::<anyhow::Result<_>>()
+            .map_err(Error::from)
     }
 }
PATCH

echo "Patch applied successfully"
