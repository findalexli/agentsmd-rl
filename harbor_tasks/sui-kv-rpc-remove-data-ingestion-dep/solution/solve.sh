#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for PR #26066
cat <<'PATCH' | git apply -
diff --git a/Cargo.lock b/Cargo.lock
index 46c85b4f8160..cfae71f08de4 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -15889,7 +15889,6 @@ dependencies = [
  "prometheus",
  "prost-types 0.14.1",
  "rustls",
- "sui-data-ingestion-core",
  "sui-futures",
  "sui-kvstore",
  "sui-package-resolver",
@@ -15897,6 +15896,7 @@ dependencies = [
  "sui-rpc",
  "sui-rpc-api",
  "sui-sdk-types",
+ "sui-storage",
  "sui-types",
  "telemetry-subscribers",
  "tokio",
diff --git a/crates/sui-kv-rpc/Cargo.toml b/crates/sui-kv-rpc/Cargo.toml
index eaa47834e8aa..ffce1fa1935e 100644
--- a/crates/sui-kv-rpc/Cargo.toml
+++ b/crates/sui-kv-rpc/Cargo.toml
@@ -17,8 +17,8 @@ prometheus.workspace = true
 rustls.workspace = true
 mysten-metrics.workspace = true
 mysten-network.workspace = true
-sui-data-ingestion-core.workspace = true
 sui-kvstore.workspace = true
+sui-storage.workspace = true
 sui-rpc-api.workspace = true
 sui-rpc.workspace = true
 sui-types.workspace = true
diff --git a/crates/sui-kv-rpc/src/v2/get_checkpoint.rs b/crates/sui-kv-rpc/src/v2/get_checkpoint.rs
index f4f824149009..6742dc0cb04e 100644
--- a/crates/sui-kv-rpc/src/v2/get_checkpoint.rs
+++ b/crates/sui-kv-rpc/src/v2/get_checkpoint.rs
@@ -1,7 +1,6 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0

-use sui_data_ingestion_core::{CheckpointReader, create_remote_store_client};
 use sui_kvstore::tables::checkpoints::col;
 use sui_kvstore::{BigTableClient, CHECKPOINTS_PIPELINE, KeyValueStoreReader};
 use sui_rpc::field::{FieldMask, FieldMaskTree, FieldMaskUtil};
@@ -11,6 +10,7 @@ use sui_rpc::proto::sui::rpc::v2::{Checkpoint, GetCheckpointRequest, GetCheckpoi
 use sui_rpc_api::{
     CheckpointNotFoundError, ErrorReason, RpcError, proto::google::rpc::bad_request::FieldViolation,
 };
+use sui_storage::object_store::util::{build_object_store, fetch_checkpoint};
 use sui_types::digests::CheckpointDigest;

 pub const READ_MASK_DEFAULT: &str = "sequence_number,digest";
@@ -93,12 +93,8 @@ pub async fn get_checkpoint(
         || read_mask.contains(Checkpoint::OBJECTS_FIELD))
         && let Some(url) = checkpoint_bucket
     {
-        let client = create_remote_store_client(url, vec![], 60)?;
-        let (checkpoint_data, _) =
-            CheckpointReader::fetch_from_object_store(&client, sequence_number).await?;
-        let checkpoint = sui_types::full_checkpoint_content::Checkpoint::from(
-            std::sync::Arc::into_inner(checkpoint_data).unwrap(),
-        );
+        let store = build_object_store(&url, vec![]);
+        let checkpoint = fetch_checkpoint(&store, sequence_number).await?;

         message.merge(&checkpoint, &read_mask);
     }
PATCH

# Verify the patch was applied by checking for a distinctive line from the new code
if grep -q "sui_storage::object_store::util::{build_object_store, fetch_checkpoint}" crates/sui-kv-rpc/src/v2/get_checkpoint.rs; then
    echo "Patch applied successfully"
else
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi
