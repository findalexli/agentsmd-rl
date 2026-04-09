#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for PR #26056
# This adds probe-before-fetch functionality for consensus commit sync
cat <<'PATCH' | git apply -
diff --git a/consensus/config/src/parameters.rs b/consensus/config/src/parameters.rs
index b08ee8d4af6e..a2b35658dfe5 100644
--- a/consensus/config/src/parameters.rs
+++ b/consensus/config/src/parameters.rs
@@ -95,6 +95,16 @@ pub struct Parameters {
     #[serde(default = "Parameters::default_commit_sync_batches_ahead")]
     pub commit_sync_batches_ahead: usize,

+    // Base per-request timeout for commit sync fetches. The actual timeout grows progressively
+    // with a multiplier to allow larger commit batches to finish downloading.
+    #[serde(default = "Parameters::default_commit_sync_request_timeout")]
+    pub commit_sync_request_timeout: Duration,
+
+    // Timeout for the connectivity probe against a peer before committing to a full fetch.
+    // Should be short to quickly skip unreachable peers.
+    #[serde(default = "Parameters::default_commit_sync_probe_timeout")]
+    pub commit_sync_probe_timeout: Duration,
+
     /// Whether to use FIFO compaction for RocksDB.
     #[serde(default = "Parameters::default_use_fifo_compaction")]
     pub use_fifo_compaction: bool,
@@ -199,6 +209,14 @@ impl Parameters {
         }
     }

+    pub(crate) fn default_commit_sync_request_timeout() -> Duration {
+        Duration::from_secs(10)
+    }
+
+    pub(crate) fn default_commit_sync_probe_timeout() -> Duration {
+        Duration::from_secs(2)
+    }
+
     pub(crate) fn default_commit_sync_batches_ahead() -> usize {
         // This is set to be a multiple of default commit_sync_parallel_fetches to allow fetching ahead,
         // while keeping the total number of inflight fetches and unprocessed fetched commits limited.
@@ -229,6 +247,8 @@ impl Default for Parameters {
             commit_sync_parallel_fetches: Parameters::default_commit_sync_parallel_fetches(),
             commit_sync_batch_size: Parameters::default_commit_sync_batch_size(),
             commit_sync_batches_ahead: Parameters::default_commit_sync_batches_ahead(),
+            commit_sync_request_timeout: Parameters::default_commit_sync_request_timeout(),
+            commit_sync_probe_timeout: Parameters::default_commit_sync_probe_timeout(),
             use_fifo_compaction: Parameters::default_use_fifo_compaction(),
             tonic: TonicParameters::default(),
             internal: InternalParameters::default(),
diff --git a/consensus/config/tests/snapshots/parameters_test__parameters.snap b/consensus/config/tests/snapshots/parameters_test__parameters.snap
index cf80822e5517..7b0574b5e1c6 100644
--- a/consensus/config/tests/snapshots/parameters_test__parameters.snap
+++ b/consensus/config/tests/snapshots/parameters_test__parameters.snap
@@ -1,5 +1,6 @@
 ---
 source: consensus/config/tests/parameters_test.rs
+assertion_line: 8
 expression: parameters
 ---
 leader_timeout:
@@ -23,6 +24,12 @@ dag_state_cached_rounds: 500
 commit_sync_parallel_fetches: 8
 commit_sync_batch_size: 100
 commit_sync_batches_ahead: 32
+commit_sync_request_timeout:
+  secs: 10
+  nanos: 0
+commit_sync_probe_timeout:
+  secs: 2
+  nanos: 0
 use_fifo_compaction: true
 tonic:
   keepalive_interval:
diff --git a/consensus/core/src/authority_service.rs b/consensus/core/src/authority_service.rs
index 11a0d26a7195..83fc85852a04 100644
--- a/consensus/core/src/authority_service.rs
+++ b/consensus/core/src/authority_service.rs
@@ -32,7 +32,10 @@ use crate::{
     core_thread::CoreThreadDispatcher,
     dag_state::DagState,
     error::{ConsensusError, ConsensusResult},
-    network::{BlockStream, ExtendedSerializedBlock, PeerId, ValidatorNetworkService},
+    network::{
+        BlockStream, ExtendedSerializedBlock, NodeId, ObserverBlockStream, ObserverNetworkService,
+        PeerId, ValidatorNetworkService,
+    },
     round_tracker::RoundTracker,
     stake_aggregator::{QuorumThreshold, StakeAggregator},
     storage::Store,
@@ -643,6 +646,40 @@ impl<C: CoreThreadDispatcher> ValidatorNetworkService for AuthorityService<C> {
     }
 }

+#[async_trait]
+impl<C: CoreThreadDispatcher> ObserverNetworkService for AuthorityService<C> {
+    async fn handle_stream_blocks(
+        &self,
+        _peer: NodeId,
+        _highest_round_per_authority: Vec<u64>,
+    ) -> ConsensusResult<ObserverBlockStream> {
+        // TODO: Implement observer block streaming
+        todo!("Observer block streaming not yet implemented")
+    }
+
+    async fn handle_fetch_blocks(
+        &self,
+        _peer: NodeId,
+        _block_refs: Vec<BlockRef>,
+    ) -> ConsensusResult<Vec<Bytes>> {
+        // TODO: implement observer fetch blocks, similar to validator fetch_blocks but
+        // without highest_accepted_rounds.
+        Err(ConsensusError::NetworkRequest(
+            "Observer fetch blocks not yet implemented".to_string(),
+        ))
+    }
+
+    async fn handle_fetch_commits(
+        &self,
+        _peer: NodeId,
+        _commit_range: CommitRange,
+    ) -> ConsensusResult<(Vec<TrustedCommit>, Vec<VerifiedBlock>)> {
+        // TODO: implement observer fetch commits, similar to validator fetch_commits.
+        Err(ConsensusError::NetworkRequest(
+            "Observer fetch commits not yet implemented".to_string(),
+        ))
+    }
+}
 struct Counter {
     count: usize,
     subscriptions_by_peer: BTreeMap<PeerId, usize>,
diff --git a/consensus/core/src/commit_syncer.rs b/consensus/core/src/commit_syncer.rs
index f817e653d8df..4a418f857ba8 100644
--- a/consensus/core/src/commit_syncer.rs
+++ b/consensus/core/src/commit_syncer.rs
@@ -436,8 +436,7 @@ where
         inner: Arc<Inner<VC, OC>>,
         commit_range: CommitRange,
     ) -> (CommitIndex, CertifiedCommits) {
-        // Individual request base timeout.
-        const TIMEOUT: Duration = Duration::from_secs(10);
+        let base_timeout = inner.context.parameters.commit_sync_request_timeout;
         // Max per-request timeout will be base timeout times a multiplier.
         // At the extreme, this means there will be 120s timeout to fetch max_blocks_per_fetch blocks.
         const MAX_TIMEOUT_MULTIPLIER: u32 = 12;
@@ -470,7 +469,7 @@ where
             target_authorities.truncate(MAX_NUM_TARGETS);
             // Increase timeout multiplier for each loop until MAX_TIMEOUT_MULTIPLIER.
             timeout_multiplier = (timeout_multiplier + 1).min(MAX_TIMEOUT_MULTIPLIER);
-            let request_timeout = TIMEOUT * timeout_multiplier;
+            let request_timeout = base_timeout * timeout_multiplier;
             // Give enough overall timeout for fetching commits and blocks.
             // - Timeout for fetching commits and commit certifying blocks.
             // - Timeout for fetching blocks referenced by the commits.
@@ -529,7 +528,7 @@ where
                 }
             }
             // Avoid busy looping, by waiting for a while before retrying.
-            sleep(TIMEOUT).await;
+            sleep(base_timeout).await;
         }
     }

@@ -549,6 +548,17 @@ where
             .commit_sync_fetch_once_latency
             .start_timer();

+        // 0. Probe the target to check reachability before committing to the full fetch.
+        // This skips unreachable and slow peers quickly.
+        let probe_timeout = inner.context.parameters.commit_sync_probe_timeout;
+        inner
+            .network_client
+            .probe_connectivity(
+                crate::network::PeerId::Validator(target_authority),
+                probe_timeout,
+            )
+            .await?;
+
         // 1. Fetch commits in the commit range from the target authority.
         let (serialized_commits, serialized_blocks) = inner
             .network_client
diff --git a/consensus/core/src/network/clients.rs b/consensus/core/src/network/clients.rs
index ccb14059e6a1..6018aab04209 100644
--- a/consensus/core/src/network/clients.rs
+++ b/consensus/core/src/network/clients.rs
@@ -123,6 +123,19 @@ where
         }
     }

+    pub async fn probe_connectivity(&self, peer: PeerId, timeout: Duration) -> ConsensusResult<()> {
+        // For now, only probe connectivity by validator against validators.
+        if self.context.is_validator()
+            && let PeerId::Validator(authority) = peer
+        {
+            let client = self.validator_client.as_ref().ok_or_else(|| {
+                ConsensusError::NetworkConfig("Validator client not available".to_string())
+            })?;
+            let _ = client.get_latest_rounds(authority, timeout).await?;
+        }
+        Ok(())
+    }
+
     pub async fn fetch_commits(
         &self,
         peer: PeerId,
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "probe_connectivity" consensus/core/src/network/clients.rs && echo "Patch applied successfully"
