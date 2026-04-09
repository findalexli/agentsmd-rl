#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch to remove certified blocks sender channel
cat <<'PATCH' | git apply -
diff --git a/consensus/core/benches/commit_finalizer_bench.rs b/consensus/core/benches/commit_finalizer_bench.rs
index 02a114992a3b..a53dd2e799bc 100644
--- a/consensus/core/benches/commit_finalizer_bench.rs
+++ b/consensus/core/benches/commit_finalizer_bench.rs
@@ -33,13 +33,10 @@ impl BenchFixture {
             Arc::new(MemStore::new()),
         )));
         let linearizer = Linearizer::new(context.clone(), dag_state.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (commit_sender, _commit_receiver) =
             monitored_mpsc::unbounded_channel("consensus_commit_output");
diff --git a/consensus/core/src/authority_node.rs b/consensus/core/src/authority_node.rs
index 90bdee167688..e83b7dc6895e 100644
--- a/consensus/core/src/authority_node.rs
+++ b/consensus/core/src/authority_node.rs
@@ -251,12 +251,8 @@ where
             transaction_verifier,
         ));

-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            commit_consumer.block_sender.clone(),
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());

         let mut proposed_block_handler = ProposedBlockHandler::new(
             context.clone(),
diff --git a/consensus/core/src/authority_service.rs b/consensus/core/src/authority_service.rs
index 83fc85852a04..f3773db07988 100644
--- a/consensus/core/src/authority_service.rs
+++ b/consensus/core/src/authority_service.rs
@@ -883,7 +883,6 @@ mod tests {
     use bytes::Bytes;
     use consensus_config::AuthorityIndex;
     use consensus_types::block::{BlockDigest, BlockRef, Round};
-    use mysten_metrics::monitored_mpsc;
     use parking_lot::{Mutex, RwLock};
     use tokio::{sync::broadcast, time::sleep};

@@ -1071,16 +1070,10 @@ mod tests {
             Some(fake_client.clone()),
             Some(fake_client.clone()),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let synchronizer = Synchronizer::start(
             network_client,
@@ -1195,16 +1188,10 @@ mod tests {
             Some(fake_client.clone()),
             Some(fake_client.clone()),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let synchronizer = Synchronizer::start(
             network_client,
@@ -1368,16 +1355,10 @@ mod tests {
             Some(fake_client.clone()),
             Some(fake_client.clone()),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let synchronizer = Synchronizer::start(
             network_client,
@@ -1446,16 +1427,10 @@ mod tests {
             Some(fake_client.clone()),
             Some(fake_client.clone()),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let synchronizer = Synchronizer::start(
             network_client,
@@ -1541,16 +1516,10 @@ mod tests {
             Some(fake_client.clone()),
             Some(fake_client.clone()),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let synchronizer = Synchronizer::start(
             network_client,
diff --git a/consensus/core/src/block.rs b/consensus/core/src/block.rs
index b1b4e19cbd1b..8af1e05c24cf 100644
--- a/consensus/core/src/block.rs
+++ b/consensus/core/src/block.rs
@@ -579,11 +579,6 @@ impl CertifiedBlock {
     }
 }

-/// A batch of certified blocks output by consensus for processing.
-pub struct CertifiedBlocksOutput {
-    pub blocks: Vec<CertifiedBlock>,
-}
-
 /// Creates fake blocks for testing.
 /// This struct is public for testing in other crates.
 #[derive(Clone)]
diff --git a/consensus/core/src/commit_consumer.rs b/consensus/core/src/commit_consumer.rs
index 68da8363f45d..f1060ea80ba9 100644
--- a/consensus/core/src/commit_consumer.rs
+++ b/consensus/core/src/commit_consumer.rs
@@ -7,7 +7,7 @@ use mysten_metrics::monitored_mpsc::{UnboundedReceiver, UnboundedSender, unbound
 use tokio::sync::watch;
 use tracing::debug;

-use crate::{CommitIndex, CommittedSubDag, block::CertifiedBlocksOutput};
+use crate::{CommitIndex, CommittedSubDag};

 /// Arguments from commit consumer to this consensus instance.
 /// This includes both parameters and components for communications.
@@ -23,9 +23,6 @@ pub struct CommitConsumerArgs {

     /// A channel to output the committed sub dags.
     pub(crate) commit_sender: UnboundedSender<CommittedSubDag>,
-    /// A channel to output blocks for processing, separated from consensus commits.
-    /// In each block output, transactions that are not rejected are considered certified.
-    pub(crate) block_sender: UnboundedSender<CertifiedBlocksOutput>,
     // Allows the commit consumer to report its progress.
     monitor: Arc<CommitConsumerMonitor>,
 }
@@ -36,7 +33,6 @@ impl CommitConsumerArgs {
         consumer_last_processed_commit_index: CommitIndex,
     ) -> (Self, UnboundedReceiver<CommittedSubDag>) {
         let (commit_sender, commit_receiver) = unbounded_channel("consensus_commit_output");
-        let (block_sender, _block_receiver) = unbounded_channel("consensus_block_output");

         let monitor = Arc::new(CommitConsumerMonitor::new(
             replay_after_commit_index,
@@ -47,7 +43,6 @@ impl CommitConsumerArgs {
                 replay_after_commit_index,
                 consumer_last_processed_commit_index,
                 commit_sender,
-                block_sender,
                 monitor,
             },
             commit_receiver,
diff --git a/consensus/core/src/commit_observer.rs b/consensus/core/src/commit_observer.rs
index fbeb7d3dc137..858e386df859 100644
--- a/consensus/core/src/commit_observer.rs
+++ b/consensus/core/src/commit_observer.rs
@@ -339,7 +339,7 @@ impl CommitObserver {
 mod tests {
     use consensus_config::AuthorityIndex;
     use consensus_types::block::BlockRef;
-    use mysten_metrics::monitored_mpsc::{UnboundedReceiver, unbounded_channel};
+    use mysten_metrics::monitored_mpsc::UnboundedReceiver;
     use parking_lot::RwLock;
     use rstest::rstest;
     use tokio::time::timeout;
@@ -369,12 +369,10 @@ mod tests {
         let last_processed_commit_index = 0;
         let (commit_consumer, mut commit_receiver) =
             CommitConsumerArgs::new(0, last_processed_commit_index);
-        let (blocks_sender, _blocks_receiver) = unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         const NUM_OF_COMMITS_PER_SCHEDULE: u64 = 5;
         let leader_schedule = Arc::new(
@@ -518,12 +516,10 @@ mod tests {
             context.clone(),
             mem_store.clone(),
         )));
-        let (blocks_sender, _blocks_receiver) = unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let last_processed_commit_index = 0;
         let (commit_consumer, mut commit_receiver) =
diff --git a/consensus/core/src/commit_syncer.rs b/consensus/core/src/commit_syncer.rs
index 4a418f857ba8..be77aa9d5db0 100644
--- a/consensus/core/src/commit_syncer.rs
+++ b/consensus/core/src/commit_syncer.rs
@@ -886,7 +886,6 @@ mod tests {
     use bytes::Bytes;
     use consensus_config::{AuthorityIndex, Parameters};
     use consensus_types::block::{BlockRef, Round};
-    use mysten_metrics::monitored_mpsc;
     use parking_lot::RwLock;

     use crate::{
@@ -1025,14 +1024,8 @@ mod tests {
         ));
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let commit_consumer_monitor = Arc::new(CommitConsumerMonitor::new(0, 0));
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
diff --git a/consensus/core/src/commit_test_fixture.rs b/consensus/core/src/commit_test_fixture.rs
index a0f620e17306..7003875cefa9 100644
--- a/consensus/core/src/commit_test_fixture.rs
+++ b/consensus/core/src/commit_test_fixture.rs
@@ -69,12 +69,10 @@ impl CommitTestFixture {
         let block_manager = BlockManager::new(context.clone(), dag_state.clone());

         let linearizer = Linearizer::new(context.clone(), dag_state.clone());
-        let (blocks_sender, _blocks_receiver) = unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (commit_sender, _commit_receiver) = unbounded_channel("consensus_commit_output");
         let commit_finalizer = CommitFinalizer::new(
diff --git a/consensus/core/src/core.rs b/consensus/core/src/core.rs
index bd90386d0361..48cb00352590 100644
--- a/consensus/core/src/core.rs
+++ b/consensus/core/src/core.rs
@@ -1472,13 +1472,10 @@ impl CoreTextFixture {
         );
         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            mysten_metrics::monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
         // Need at least one subscriber to the block broadcast channel.
@@ -1539,7 +1536,6 @@ mod test {
     use consensus_config::{AuthorityIndex, Parameters};
     use consensus_types::block::TransactionIndex;
     use futures::{StreamExt, stream::FuturesUnordered};
-    use mysten_metrics::monitored_mpsc;
     use tokio::time::sleep;

     use super::*;
@@ -1602,13 +1598,10 @@ mod test {
             context.clone(),
             dag_state.clone(),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );

         let (commit_consumer, _commit_receiver) = CommitConsumerArgs::new(0, 0);
@@ -1628,13 +1621,10 @@ mod test {

         // Now spin up core
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         transaction_certifier.recover_blocks_after_round(dag_state.read().gc_round());
         // Need at least one subscriber to the block broadcast channel.
@@ -1742,13 +1732,10 @@ mod test {
             context.clone(),
             dag_state.clone(),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );

         let (commit_consumer, _commit_receiver) = CommitConsumerArgs::new(0, 0);
@@ -1768,13 +1755,10 @@ mod test {

         // Now spin up core
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         transaction_certifier.recover_blocks_after_round(dag_state.read().gc_round());
         // Need at least one subscriber to the block broadcast channel.
@@ -1852,13 +1836,10 @@ mod test {
         let block_manager = BlockManager::new(context.clone(), dag_state.clone());
         let (transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
         // Need at least one subscriber to the block broadcast channel.
@@ -2085,13 +2066,10 @@ mod test {
             context.clone(),
             dag_state.clone(),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );

         let (commit_consumer, _commit_receiver) = CommitConsumerArgs::new(0, 0);
@@ -2114,13 +2092,10 @@ mod test {

         // Now recover Core and other components.
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         transaction_certifier.recover_blocks_after_round(dag_state.read().gc_round());
         // Need at least one subscriber to the block broadcast channel.
@@ -2250,13 +2225,10 @@ mod test {
             context.clone(),
             dag_state.clone(),
         ));
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );

         let (commit_consumer, _commit_receiver) = CommitConsumerArgs::new(0, 0);
@@ -2279,13 +2251,10 @@ mod test {

         // Now spin up core
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         // Need at least one subscriber to the block broadcast channel.
         let _block_receiver = signal_receivers.block_broadcast_receiver();
@@ -2347,13 +2316,10 @@ mod test {
         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         // Need at least one subscriber to the block broadcast channel.
         let _block_receiver = signal_receivers.block_broadcast_receiver();
@@ -2703,13 +2669,10 @@ mod test {

         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
         // Need at least one subscriber to the block broadcast channel.
@@ -3002,13 +2965,10 @@ mod test {

         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
         // Need at least one subscriber to the block broadcast channel.
@@ -3099,13 +3059,10 @@ mod test {
         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         // Need at least one subscriber to the block broadcast channel.
         let _block_receiver = signal_receivers.block_broadcast_receiver();
@@ -3547,13 +3504,10 @@ mod test {
         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         // Need at least one subscriber to the block broadcast channel.
         let _block_receiver = signal_receivers.block_broadcast_receiver();
diff --git a/consensus/core/src/core_thread.rs b/consensus/core/src/core_thread.rs
index c7482a990fc3..33889ef13f4e 100644
--- a/consensus/core/src/core_thread.rs
+++ b/consensus/core/src/core_thread.rs
@@ -372,7 +372,6 @@ impl CoreThreadDispatcher for MockCoreThreadDispatcher {

 #[cfg(test)]
 mod test {
-    use mysten_metrics::monitored_mpsc;
     use parking_lot::RwLock;

     use super::*;
@@ -401,13 +400,10 @@ mod test {
         let block_manager = BlockManager::new(context.clone(), dag_state.clone());
         let (_transaction_client, tx_receiver) = TransactionClient::new(context.clone());
         let transaction_consumer = TransactionConsumer::new(tx_receiver, context.clone());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let transaction_certifier = TransactionCertifier::new(
             context.clone(),
             Arc::new(NoopBlockVerifier {}),
             dag_state.clone(),
-            blocks_sender,
         );
         let (signals, signal_receivers) = CoreSignals::new(context.clone());
         let _block_receiver = signal_receivers.block_broadcast_receiver();
diff --git a/consensus/core/src/lib.rs b/consensus/core/src/lib.rs
index 67b6757e2a58..3172f253a7af 100644
--- a/consensus/core/src/lib.rs
+++ b/consensus/core/src/lib.rs
@@ -54,7 +54,7 @@ mod randomized_tests;

 /// Exported Consensus API.
 pub use authority_node::{ConsensusAuthority, NetworkType};
-pub use block::{BlockAPI, CertifiedBlock, CertifiedBlocksOutput};
+pub use block::{BlockAPI, CertifiedBlock};

 /// Exported API for testing and tools.
 pub use block::{TestBlock, Transaction, VerifiedBlock};
diff --git a/consensus/core/src/synchronizer.rs b/consensus/core/src/synchronizer.rs
index 9d4f92e528c2..d42bc76ebbb9 100644
--- a/consensus/core/src/synchronizer.rs
+++ b/consensus/core/src/synchronizer.rs
@@ -1483,16 +1483,10 @@ mod tests {
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let mock_client = Arc::new(MockNetworkClient::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));

         let network_client = Arc::new(SynchronizerClient::new(
@@ -1547,16 +1541,10 @@ mod tests {
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
         let mock_client = Arc::new(MockNetworkClient::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));

         let network_client = Arc::new(SynchronizerClient::new(
@@ -1622,16 +1610,10 @@ mod tests {
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
         let mock_client = Arc::new(MockNetworkClient::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));

         // Create some test blocks
@@ -1708,16 +1690,10 @@ mod tests {
         let block_verifier = Arc::new(NoopBlockVerifier {});
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
         let mock_client = Arc::new(MockNetworkClient::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));

@@ -1847,17 +1823,11 @@ mod tests {
         let block_verifier = Arc::new(NoopBlockVerifier {});
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
         let mock_client = Arc::new(MockNetworkClient::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let our_index = AuthorityIndex::new_for_test(0);

@@ -1978,17 +1948,11 @@ mod tests {
         let context = Arc::new(context);
         let block_verifier = Arc::new(NoopBlockVerifier {});
         let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
-        let (blocks_sender, _blocks_receiver) =
-            monitored_mpsc::unbounded_channel("consensus_block_output");
         let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
         let store = Arc::new(MemStore::new());
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store)));
-        let transaction_certifier = TransactionCertifier::new(
-            context.clone(),
-            block_verifier.clone(),
-            dag_state.clone(),
-            blocks_sender,
-        );
+        let transaction_certifier =
+            TransactionCertifier::new(context.clone(), block_verifier.clone(), dag_state.clone());
         let round_tracker = Arc::new(RwLock::new(RoundTracker::new(context.clone(), vec![])));
         let (commands_sender, _commands_receiver) =
             monitored_mpsc::channel("consensus_synchronizer_commands", 1000);
diff --git a/consensus/core/src/transaction_certifier.rs b/consensus/core/src/transaction_certifier.rs
index b08f8e8d0e57..a62aaa4e624d 100644
--- a/consensus/core/src/transaction_certifier.rs
+++ b/consensus/core/src/transaction_certifier.rs
@@ -5,12 +5,11 @@ use std::{collections::BTreeMap, sync::Arc, time::Duration};

 use consensus_config::Stake;
 use consensus_types::block::{BlockRef, Round, TransactionIndex};
-use mysten_metrics::monitored_mpsc::UnboundedSender;
 use parking_lot::RwLock;
 use tracing::{debug, info};

 use crate::{
-    BlockAPI as _, CertifiedBlock, CertifiedBlocksOutput, VerifiedBlock,
+    BlockAPI as _, CertifiedBlock, VerifiedBlock,
     block::{BlockTransactionVotes, GENESIS_ROUND},
     block_verifier::BlockVerifier,
     context::Context,
@@ -52,8 +51,6 @@ pub struct TransactionCertifier {
     block_verifier: Arc<dyn BlockVerifier>,
     // The state of the DAG.
     dag_state: Arc<RwLock<DagState>>,
-    // An unbounded channel to output certified blocks to Sui consensus block handler.
-    certified_blocks_sender: UnboundedSender<CertifiedBlocksOutput>,
 }

 impl TransactionCertifier {
@@ -61,13 +58,11 @@ impl TransactionCertifier {
         context: Arc<Context>,
         block_verifier: Arc<dyn BlockVerifier>,
         dag_state: Arc<RwLock<DagState>>,
-        certified_blocks_sender: UnboundedSender<CertifiedBlocksOutput>,
     ) -> Self {
         Self {
             certifier_state: Arc::new(RwLock::new(CertifierState::new(context))),
             block_verifier,
             dag_state,
-            certified_blocks_sender,
         }
     }

@@ -158,32 +153,15 @@ impl TransactionCertifier {
     }

     /// Stores own reject votes on input blocks, and aggregates reject votes from the input blocks.
-    /// Newly certified blocks are sent to the fastpath output channel.
     pub fn add_voted_blocks(&self, voted_blocks: Vec<(VerifiedBlock, Vec<TransactionIndex>)>) {
-        let certified_blocks = self.certifier_state.write().add_voted_blocks(voted_blocks);
-        self.send_certified_blocks(certified_blocks);
+        self.certifier_state.write().add_voted_blocks(voted_blocks);
     }

     /// Aggregates accept votes from the own proposed block.
-    /// Newly certified blocks are sent to the fastpath output channel.
     pub(crate) fn add_proposed_block(&self, proposed_block: VerifiedBlock) {
-        let certified_blocks = self
-            .certifier_state
+        self.certifier_state
             .write()
             .add_proposed_block(proposed_block);
-        self.send_certified_blocks(certified_blocks);
-    }
-
-    // Sends certified blocks to the fastpath output channel.
-    fn send_certified_blocks(&self, certified_blocks: Vec<CertifiedBlock>) {
-        if certified_blocks.is_empty() {
-            return;
-        }
-        if let Err(e) = self.certified_blocks_sender.send(CertifiedBlocksOutput {
-            blocks: certified_blocks,
-        }) {
-            tracing::warn!("Failed to send certified blocks: {:?}", e);
-        }
     }

     /// Retrieves own votes on peer block transactions.
PATCH

# Verify the patch was applied and distinctive line removed
grep -q "certified_blocks_sender: UnboundedSender" consensus/core/src/transaction_certifier.rs && echo "Patch failed: certified_blocks_sender still exists" && exit 1

echo "Patch applied successfully"
