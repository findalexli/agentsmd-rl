#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "always_accept_system_transactions: bool" consensus/config/src/consensus_protocol_config.rs 2>/dev/null; then
    echo "Applying cleanup patch..."
else
    echo "Patch already applied or file already cleaned"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/consensus/config/src/consensus_protocol_config.rs b/consensus/config/src/consensus_protocol_config.rs
index f1ccdc705cce..3ac3810d19dd 100644
--- a/consensus/config/src/consensus_protocol_config.rs
+++ b/consensus/config/src/consensus_protocol_config.rs
@@ -25,7 +25,6 @@ pub struct ConsensusProtocolConfig {
     transaction_voting_enabled: bool,
     num_leaders_per_round: Option<usize>,
     bad_nodes_stake_threshold: u64,
-    always_accept_system_transactions: bool,
 }

 impl Default for ConsensusProtocolConfig {
@@ -40,7 +39,6 @@ impl Default for ConsensusProtocolConfig {
             transaction_voting_enabled: false,
             num_leaders_per_round: None,
             bad_nodes_stake_threshold: 0,
-            always_accept_system_transactions: false,
         }
     }
 }
@@ -56,7 +54,6 @@ impl ConsensusProtocolConfig {
         transaction_voting_enabled: bool,
         num_leaders_per_round: Option<usize>,
         bad_nodes_stake_threshold: u64,
-        always_accept_system_transactions: bool,
     ) -> Self {
         Self {
             protocol_version,
@@ -68,7 +65,6 @@ impl ConsensusProtocolConfig {
             transaction_voting_enabled,
             num_leaders_per_round,
             bad_nodes_stake_threshold,
-            always_accept_system_transactions,
         }
     }

@@ -85,7 +81,6 @@ impl ConsensusProtocolConfig {
             transaction_voting_enabled: true,
             num_leaders_per_round: Some(1),
             bad_nodes_stake_threshold: 30,
-            always_accept_system_transactions: true,
         }
     }

@@ -127,10 +122,6 @@ impl ConsensusProtocolConfig {
         self.bad_nodes_stake_threshold
     }

-    pub fn always_accept_system_transactions(&self) -> bool {
-        self.always_accept_system_transactions
-    }
-
     // Test setter methods

     pub fn set_gc_depth_for_testing(&mut self, val: u32) {
diff --git a/consensus/core/src/commit.rs b/consensus/core/src/commit.rs
index 77dcef31a56a..d7e69758125b 100644
--- a/consensus/core/src/commit.rs
+++ b/consensus/core/src/commit.rs
@@ -20,7 +20,6 @@ use serde::{Deserialize, Serialize};

 use crate::{
     block::{BlockAPI, Slot, VerifiedBlock},
-    context::Context,
     leader_scoring::ReputationScores,
     storage::Store,
 };
@@ -380,8 +379,6 @@ pub struct CommittedSubDag {
     ///
     /// Indices of rejected transactions in each block.
     pub rejected_transactions_by_block: BTreeMap<BlockRef, Vec<TransactionIndex>>,
-    /// Used by consensus to communicate whether to always accept system transactions in this commit.
-    pub always_accept_system_transactions: bool,
 }

 impl CommittedSubDag {
@@ -391,7 +388,6 @@ impl CommittedSubDag {
         blocks: Vec<VerifiedBlock>,
         timestamp_ms: BlockTimestampMs,
         commit_ref: CommitRef,
-        always_accept_system_transactions: bool,
     ) -> Self {
         Self {
             leader,
@@ -402,7 +398,6 @@ impl CommittedSubDag {
             recovered_rejected_transactions: false,
             reputation_scores_desc: vec![],
             rejected_transactions_by_block: BTreeMap::new(),
-            always_accept_system_transactions,
         }
     }
 }
@@ -464,7 +459,6 @@ impl fmt::Debug for CommittedSubDag {

 // Recovers the full CommittedSubDag from block store, based on Commit.
 pub(crate) fn load_committed_subdag_from_store(
-    context: &Arc<Context>,
     store: &dyn Store,
     commit: TrustedCommit,
     reputation_scores_desc: Vec<(AuthorityIndex, u64)>,
@@ -493,7 +487,6 @@ pub(crate) fn load_committed_subdag_from_store(
         blocks,
         commit.timestamp_ms(),
         commit.reference(),
-        context.protocol_config.always_accept_system_transactions(),
     );

     subdag.reputation_scores_desc = reputation_scores_desc;
@@ -779,8 +772,7 @@ mod tests {
             leader_ref,
             blocks.clone(),
         );
-        let subdag =
-            load_committed_subdag_from_store(&context, store.as_ref(), commit.clone(), vec![]);
+        let subdag = load_committed_subdag_from_store(store.as_ref(), commit.clone(), vec![]);
         assert_eq!(subdag.leader, leader_ref);
         assert_eq!(subdag.timestamp_ms, leader_block.timestamp_ms());
         assert_eq!(
diff --git a/consensus/core/src/commit_observer.rs b/consensus/core/src/commit_observer.rs
index 67dc07b58739..fbeb7d3dc137 100644
--- a/consensus/core/src/commit_observer.rs
+++ b/consensus/core/src/commit_observer.rs
@@ -240,7 +240,6 @@ impl CommitObserver {
                 };

                 let committed_sub_dag = load_committed_subdag_from_store(
-                    &self.context,
                     self.store.as_ref(),
                     commit,
                     reputation_scores,
diff --git a/consensus/core/src/dag_state.rs b/consensus/core/src/dag_state.rs
index 801a0229993c..fd04e841ec75 100644
--- a/consensus/core/src/dag_state.rs
+++ b/consensus/core/src/dag_state.rs
@@ -147,12 +147,8 @@ impl DagState {
                         last_committed_rounds[block_ref.author] =
                             max(last_committed_rounds[block_ref.author], block_ref.round);
                     }
-                    let committed_subdag = load_committed_subdag_from_store(
-                        &context,
-                        store.as_ref(),
-                        commit.clone(),
-                        vec![],
-                    );
+                    let committed_subdag =
+                        load_committed_subdag_from_store(store.as_ref(), commit.clone(), vec![]);
                     // We don't need to recover reputation scores for unscored_committed_subdags
                     unscored_committed_subdags.push(committed_subdag);
                 });
diff --git a/consensus/core/src/leader_schedule.rs b/consensus/core/src/leader_schedule.rs
index 452f666c7249..bb67b1a077ab 100644
--- a/consensus/core/src/leader_schedule.rs
+++ b/consensus/core/src/leader_schedule.rs
@@ -674,7 +674,6 @@ mod tests {
             vec![],
             context.clock.timestamp_utc_ms(),
             CommitRef::new(1, CommitDigest::MIN),
-            true,
         )];
         dag_state.write().add_scoring_subdags(unscored_subdags);

@@ -770,7 +769,6 @@ mod tests {
             blocks,
             context.clock.timestamp_utc_ms(),
             last_commit.reference(),
-            true,
         )];

         let mut dag_state_write = dag_state.write();
diff --git a/consensus/core/src/linearizer.rs b/consensus/core/src/linearizer.rs
index 5b3045b50925..8be55a18be34 100644
--- a/consensus/core/src/linearizer.rs
+++ b/consensus/core/src/linearizer.rs
@@ -114,9 +114,6 @@ impl Linearizer {
             to_commit,
             timestamp_ms,
             commit.reference(),
-            self.context
-                .protocol_config
-                .always_accept_system_transactions(),
         );

         (sub_dag, commit)
diff --git a/consensus/core/src/test_dag_builder.rs b/consensus/core/src/test_dag_builder.rs
index c2f06e112d5e..557f96b23171 100644
--- a/consensus/core/src/test_dag_builder.rs
+++ b/consensus/core/src/test_dag_builder.rs
@@ -246,7 +246,6 @@ impl DagBuilder {
                 to_commit,
                 last_timestamp_ms,
                 commit.reference(),
-                true,
             );

             self.committed_sub_dags.push((sub_dag, commit));
diff --git a/crates/sui-core/src/authority.rs b/crates/sui-core/src/authority.rs
index bef0438a08d9..03bebb68b591 100644
--- a/crates/sui-core/src/authority.rs
+++ b/crates/sui-core/src/authority.rs
@@ -138,7 +138,7 @@ use sui_types::effects::{
     TransactionEvents, VerifiedSignedTransactionEffects,
 };
 use sui_types::error::{ExecutionError, ExecutionErrorTrait, SuiErrorKind, UserInputError};
-use sui_types::event::{Event, EventID};
+use sui_types::event::EventID;
 use sui_types::executable_transaction::VerifiedExecutableTransaction;
 use sui_types::execution_status::ExecutionErrorKind;
 use sui_types::gas::{GasCostSummary, SuiGasStatus};
diff --git a/crates/sui-core/src/authority/authority_store_tables.rs b/crates/sui-core/src/authority/authority_store_tables.rs
index b186c0fe4de7..28121876a5f8 100644
--- a/crates/sui-core/src/authority/authority_store_tables.rs
+++ b/crates/sui-core/src/authority/authority_store_tables.rs
@@ -10,7 +10,6 @@ use serde::{Deserialize, Serialize};
 use std::path::Path;
 use std::sync::atomic::AtomicU64;
 use sui_types::base_types::SequenceNumber;
-use sui_types::digests::TransactionEventsDigest;
 use sui_types::effects::{TransactionEffects, TransactionEvents};
 use sui_types::global_state_hash::GlobalStateHash;
 use sui_types::storage::MarkerValue;
@@ -95,10 +94,6 @@ pub struct AuthorityPerpetualTables {
     /// tables.
     pub(crate) executed_effects: DBMap<TransactionDigest, TransactionEffectsDigest>,

-    #[allow(dead_code)]
-    #[deprecated]
-    events: DBMap<(TransactionEventsDigest, usize), Event>,
-
     // Events keyed by the digest of the transaction that produced them.
     pub(crate) events_2: DBMap<TransactionDigest, TransactionEvents>,

diff --git a/crates/sui-core/src/consensus_handler.rs b/crates/sui-core/src/consensus_handler.rs
index ef27c45e8fe3..6b68b449b973 100644
--- a/crates/sui-core/src/consensus_handler.rs
+++ b/crates/sui-core/src/consensus_handler.rs
@@ -3809,7 +3809,6 @@ mod tests {
             blocks.clone(),
             leader_block.timestamp_ms(),
             CommitRef::new(10, CommitDigest::MIN),
-            true,
         );

         // Test that the consensus handler respects backpressure.
@@ -3985,7 +3984,6 @@ mod tests {
             vec![block.clone()],
             block.timestamp_ms(),
             CommitRef::new(10, CommitDigest::MIN),
-            true,
         );

         let metrics = Arc::new(AuthorityMetrics::new(&Registry::new()));
@@ -4111,7 +4109,6 @@ mod tests {
             vec![block.clone()],
             block.timestamp_ms(),
             CommitRef::new(10, CommitDigest::MIN),
-            true,
         );

         let metrics = Arc::new(AuthorityMetrics::new(&Registry::new()));
diff --git a/crates/sui-core/src/consensus_manager/mod.rs b/crates/sui-core/src/consensus_manager/mod.rs
index 4c70d5b41787..79869201a16e 100644
--- a/crates/sui-core/src/consensus_manager/mod.rs
+++ b/crates/sui-core/src/consensus_manager/mod.rs
@@ -133,7 +133,6 @@ fn to_consensus_protocol_config(config: &ProtocolConfig, chain: Chain) -> Consen
         config.mysticeti_fastpath(),
         config.mysticeti_num_leaders_per_round(),
         config.consensus_bad_nodes_stake_threshold(),
-        config.consensus_always_accept_system_transactions(),
     )
 }

diff --git a/crates/sui-core/src/consensus_types/consensus_output_api.rs b/crates/sui-core/src/consensus_types/consensus_output_api.rs
index 2033745c016d..e5ca58cc14b6 100644
--- a/crates/sui-core/src/consensus_types/consensus_output_api.rs
+++ b/crates/sui-core/src/consensus_types/consensus_output_api.rs
@@ -89,11 +89,7 @@ impl ConsensusCommitAPI for consensus_core::CommittedSubDag {
                     .unwrap_or(&no_transaction);
                 (
                     block.reference(),
-                    parse_block_transactions(
-                        block,
-                        rejected_transactions,
-                        self.always_accept_system_transactions,
-                    ),
+                    parse_block_transactions(block, rejected_transactions),
                 )
             })
             .collect()
@@ -128,13 +124,10 @@ impl ConsensusCommitAPI for consensus_core::CommittedSubDag {
 pub(crate) fn parse_block_transactions(
     block: &VerifiedBlock,
     rejected_transactions: &[TransactionIndex],
-    always_accept_system_transactions: bool,
 ) -> Vec<ParsedTransaction> {
     let round = block.round();
     let authority = block.author().value() as AuthorityIndex;

-    // rejected_transactions contains sorted indices and can be checked more efficiently.
-    // But for simplicity, check rejection status from a BTreeSet.
     let rejected_transaction_indices = BTreeSet::from_iter(rejected_transactions.iter().cloned());
     block
         .transactions()
@@ -146,7 +139,8 @@ pub(crate) fn parse_block_transactions(
                     panic!("Failed to deserialize sequenced consensus transaction(this should not happen) {err} from {authority} at {round}");
                 },
             };
-            let rejected = rejected_transaction_indices.contains(&(index as TransactionIndex)) && (transaction.is_user_transaction() || !always_accept_system_transactions);
+            // System transactions are always accepted; only user transactions can be rejected.
+            let rejected = transaction.is_user_transaction() && rejected_transaction_indices.contains(&(index as TransactionIndex));
             ParsedTransaction {
                 transaction,
                 rejected,
PATCH

echo "Patch applied successfully"
