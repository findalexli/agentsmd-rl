#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "testing = \[\]" crates/sui-types/Cargo.toml 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index a4d7502214013..203fd51eb04f1 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -101,6 +101,10 @@ sui/
    - Move VM executes smart contracts with gas metering
    - Parallel execution for non-conflicting transactions

+### Test-Only Code
+
+Use `#[cfg(test)]` for test-only code used within the same crate. Use `#[cfg(feature = "testing")]` for test-only code that must be callable cross-crate. For the `testing` feature: define `testing = []` in the crate's `Cargo.toml`, and callers must propagate it via `features = ["testing"]` in their dependency declaration.
+
 ### Critical Development Notes
 1. **Testing Requirements**:
    - Always run tests before submitting changes
diff --git a/crates/sui-adapter-transactional-tests/Cargo.toml b/crates/sui-adapter-transactional-tests/Cargo.toml
index 50850c47cebe7..6c7574a0f96a0 100644
--- a/crates/sui-adapter-transactional-tests/Cargo.toml
+++ b/crates/sui-adapter-transactional-tests/Cargo.toml
@@ -9,7 +9,7 @@ edition = "2024"

 [dev-dependencies]
 datatest-stable.workspace = true
-sui-transactional-test-runner.workspace = true
+sui-transactional-test-runner = { workspace = true, features = ["testing"] }

 [[test]]
 name = "tests"
diff --git a/crates/sui-indexer-alt-e2e-tests/Cargo.toml b/crates/sui-indexer-alt-e2e-tests/Cargo.toml
index 1b1ae963fb688..fc281a4ccad35 100644
--- a/crates/sui-indexer-alt-e2e-tests/Cargo.toml
+++ b/crates/sui-indexer-alt-e2e-tests/Cargo.toml
@@ -72,6 +72,6 @@ sui-macros.workspace = true
 sui-sdk.workspace = true
 sui-swarm-config.workspace = true
 sui-test-transaction-builder.workspace = true
-sui-transactional-test-runner.workspace = true
+sui-transactional-test-runner = { workspace = true, features = ["testing"] }
 test-cluster.workspace = true
 tracing.workspace = true
diff --git a/crates/sui-transactional-test-runner/Cargo.toml b/crates/sui-transactional-test-runner/Cargo.toml
index 16bf5788d8052..d8e61f5e1e65c 100644
--- a/crates/sui-transactional-test-runner/Cargo.toml
+++ b/crates/sui-transactional-test-runner/Cargo.toml
@@ -61,5 +61,12 @@ sui-framework-snapshot.workspace = true
 sui-storage.workspace = true
 typed-store.workspace = true

+[[bin]]
+name = "sui-transactional-test-runner"
+required-features = ["testing"]
+
+[features]
+testing = ["sui-types/testing"]
+
 [target.'cfg(msim)'.dependencies]
 msim.workspace = true
diff --git a/crates/sui-transactional-test-runner/src/lib.rs b/crates/sui-transactional-test-runner/src/lib.rs
index c79148d080209..76d5520f35118 100644
--- a/crates/sui-transactional-test-runner/src/lib.rs
+++ b/crates/sui-transactional-test-runner/src/lib.rs
@@ -3,55 +3,71 @@

 //! This module contains the transactional test runner instantiation for the Sui adapter

+#[cfg(feature = "testing")]
 pub mod args;
+#[cfg(feature = "testing")]
 pub mod cursor;
+#[cfg(feature = "testing")]
 pub mod offchain_state;
+#[cfg(feature = "testing")]
 pub mod programmable_transaction_test_parser;
+#[cfg(feature = "testing")]
 mod simulator_persisted_store;
+#[cfg(feature = "testing")]
 pub mod test_adapter;

+#[cfg(feature = "testing")]
 pub use move_transactional_test_runner::framework::{
     create_adapter, run_tasks_with_adapter, run_test_impl,
 };
-use rand::rngs::StdRng;
-use simulacrum::AdvanceEpochConfig;
-use simulacrum::Simulacrum;
-use simulacrum::SimulatorStore;
-use simulator_persisted_store::PersistedStore;
-use std::path::Path;
-use std::sync::Arc;
-use sui_core::authority::AuthorityState;
-use sui_core::authority::authority_per_epoch_store::CertLockGuard;
-use sui_core::authority::authority_test_utils::submit_and_execute_with_error;
-use sui_core::authority::shared_object_version_manager::AssignedVersions;
-use sui_json_rpc::authority_state::StateRead;
-use sui_json_rpc_types::EventFilter;
-use sui_json_rpc_types::{DevInspectResults, DryRunTransactionBlockResponse};
-use sui_storage::key_value_store::TransactionKeyValueStore;
-use sui_types::base_types::ObjectID;
-use sui_types::base_types::SuiAddress;
-use sui_types::base_types::VersionNumber;
-use sui_types::committee::EpochId;
-use sui_types::digests::TransactionDigest;
-use sui_types::effects::TransactionEffects;
-use sui_types::effects::TransactionEvents;
-use sui_types::error::ExecutionError;
-use sui_types::error::SuiErrorKind;
-use sui_types::error::SuiResult;
-use sui_types::event::Event;
-use sui_types::executable_transaction::{ExecutableTransaction, VerifiedExecutableTransaction};
-use sui_types::messages_checkpoint::CheckpointContentsDigest;
-use sui_types::messages_checkpoint::VerifiedCheckpoint;
-use sui_types::object::Object;
-use sui_types::storage::ObjectStore;
-use sui_types::storage::ReadStore;
-use sui_types::sui_system_state::SuiSystemStateTrait;
-use sui_types::sui_system_state::epoch_start_sui_system_state::EpochStartSystemStateTrait;
-use sui_types::transaction::Transaction;
-use sui_types::transaction::TransactionKind;
-use sui_types::transaction::{InputObjects, TransactionData};
-use test_adapter::{PRE_COMPILED, SuiTestAdapter};

+#[cfg(feature = "testing")]
+mod testing_imports {
+    pub use super::simulator_persisted_store::PersistedStore;
+    pub use super::test_adapter::{PRE_COMPILED, SuiTestAdapter};
+    pub use rand::rngs::StdRng;
+    pub use simulacrum::AdvanceEpochConfig;
+    pub use simulacrum::Simulacrum;
+    pub use simulacrum::SimulatorStore;
+    pub use std::path::Path;
+    pub use std::sync::Arc;
+    pub use sui_core::authority::AuthorityState;
+    pub use sui_core::authority::authority_per_epoch_store::CertLockGuard;
+    pub use sui_core::authority::authority_test_utils::submit_and_execute_with_error;
+    pub use sui_core::authority::shared_object_version_manager::AssignedVersions;
+    pub use sui_json_rpc::authority_state::StateRead;
+    pub use sui_json_rpc_types::EventFilter;
+    pub use sui_json_rpc_types::{DevInspectResults, DryRunTransactionBlockResponse};
+    pub use sui_storage::key_value_store::TransactionKeyValueStore;
+    pub use sui_types::base_types::ObjectID;
+    pub use sui_types::base_types::SuiAddress;
+    pub use sui_types::base_types::VersionNumber;
+    pub use sui_types::committee::EpochId;
+    pub use sui_types::digests::TransactionDigest;
+    pub use sui_types::effects::TransactionEffects;
+    pub use sui_types::effects::TransactionEvents;
+    pub use sui_types::error::ExecutionError;
+    pub use sui_types::error::SuiErrorKind;
+    pub use sui_types::error::SuiResult;
+    pub use sui_types::event::Event;
+    pub use sui_types::executable_transaction::{
+        ExecutableTransaction, VerifiedExecutableTransaction,
+    };
+    pub use sui_types::messages_checkpoint::CheckpointContentsDigest;
+    pub use sui_types::messages_checkpoint::VerifiedCheckpoint;
+    pub use sui_types::object::Object;
+    pub use sui_types::storage::ObjectStore;
+    pub use sui_types::storage::ReadStore;
+    pub use sui_types::sui_system_state::SuiSystemStateTrait;
+    pub use sui_types::sui_system_state::epoch_start_sui_system_state::EpochStartSystemStateTrait;
+    pub use sui_types::transaction::Transaction;
+    pub use sui_types::transaction::TransactionKind;
+    pub use sui_types::transaction::{InputObjects, TransactionData};
+}
+#[cfg(feature = "testing")]
+use testing_imports::*;
+
+#[cfg(feature = "testing")]
 #[cfg_attr(not(msim), tokio::main)]
 #[cfg_attr(msim, msim::main)]
 pub async fn run_test(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
@@ -63,6 +79,7 @@ pub async fn run_test(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
     Ok(())
 }

+#[cfg(feature = "testing")]
 pub struct ValidatorWithFullnode {
     pub validator: Arc<AuthorityState>,
     pub fullnode: Arc<AuthorityState>,
@@ -71,6 +88,7 @@ pub struct ValidatorWithFullnode {
     next_checkpoint_seq: u64,
 }

+#[cfg(feature = "testing")]
 #[allow(unused_variables)]
 /// TODO: better name?
 #[async_trait::async_trait]
@@ -131,6 +149,7 @@ pub trait TransactionalAdapter: Send + Sync + ReadStore {
     fn get_object(&self, object_id: &ObjectID) -> Option<Object>;
 }

+#[cfg(feature = "testing")]
 #[async_trait::async_trait]
 impl TransactionalAdapter for ValidatorWithFullnode {
     async fn execute_txn(
@@ -302,6 +321,7 @@ impl TransactionalAdapter for ValidatorWithFullnode {
     }
 }

+#[cfg(feature = "testing")]
 impl ReadStore for ValidatorWithFullnode {
     fn get_committee(
         &self,
@@ -428,6 +448,7 @@ impl ReadStore for ValidatorWithFullnode {
     }
 }

+#[cfg(feature = "testing")]
 impl ObjectStore for ValidatorWithFullnode {
     fn get_object(&self, object_id: &ObjectID) -> Option<Object> {
         self.validator.get_object_store().get_object(object_id)
@@ -440,6 +461,7 @@ impl ObjectStore for ValidatorWithFullnode {
     }
 }

+#[cfg(feature = "testing")]
 #[async_trait::async_trait]
 impl TransactionalAdapter for Simulacrum<StdRng, PersistedStore> {
     async fn execute_txn(
diff --git a/crates/sui-transactional-test-runner/src/test_adapter.rs b/crates/sui-transactional-test-runner/src/test_adapter.rs
index 578395cf1cadc..167c3d070387c 100644
--- a/crates/sui-transactional-test-runner/src/test_adapter.rs
+++ b/crates/sui-transactional-test-runner/src/test_adapter.rs
@@ -498,7 +498,6 @@ impl MoveTestAdapter<'_> for SuiTestAdapter {

         let object_ids = objects.iter().map(|obj| obj.id()).collect::<Vec<_>>();

-        #[cfg(debug_assertions)]
         sui_types::transaction::clear_gasless_tokens_for_testing();

         let mut test_adapter = Self {
@@ -853,23 +852,15 @@ impl MoveTestAdapter<'_> for SuiTestAdapter {
                 token_type,
                 min_transfer,
             }) => {
-                #[cfg(debug_assertions)]
-                {
-                    let state = self.compiled_state();
-                    let type_tag = token_type
-                        .into_type_tag(&|s| Some(state.resolve_named_address(s)))
-                        .map_err(|e| anyhow::anyhow!("invalid gasless token type: {e}"))?;
-                    sui_types::transaction::add_gasless_token_for_testing(
-                        type_tag.to_canonical_string(true),
-                        min_transfer,
-                    );
-                    Ok(None)
-                }
-                #[cfg(not(debug_assertions))]
-                {
-                    let _ = (token_type, min_transfer);
-                    panic!("gasless-allow-token is only supported in debug builds")
-                }
+                let state = self.compiled_state();
+                let type_tag = token_type
+                    .into_type_tag(&|s| Some(state.resolve_named_address(s)))
+                    .map_err(|e| anyhow::anyhow!("invalid gasless token type: {e}"))?;
+                sui_types::transaction::add_gasless_token_for_testing(
+                    type_tag.to_canonical_string(true),
+                    min_transfer,
+                );
+                Ok(None)
             }
             SuiSubcommand::ViewCheckpoint => {
                 let latest_chk = self.executor.get_latest_checkpoint_sequence_number()?;
diff --git a/crates/sui-types/Cargo.toml b/crates/sui-types/Cargo.toml
index 26aa2d8bb4c58..629c89a906dd7 100644
--- a/crates/sui-types/Cargo.toml
+++ b/crates/sui-types/Cargo.toml
@@ -118,5 +118,6 @@ harness = false

 [features]
 default = []
+testing = []
 tracing = ["move-vm-profiler/tracing"]
 fuzzing = ["move-core-types/fuzzing"]
diff --git a/crates/sui-types/src/transaction.rs b/crates/sui-types/src/transaction.rs
index 774b5f9319363..cb1bd239d630f 100644
--- a/crates/sui-types/src/transaction.rs
+++ b/crates/sui-types/src/transaction.rs
@@ -970,10 +970,10 @@ pub struct ProgrammableTransaction {
     pub commands: Vec<Command>,
 }

-#[cfg(debug_assertions)]
+#[cfg(feature = "testing")]
 static GASLESS_TOKENS_FOR_TESTING: RwLock<Vec<(String, u64)>> = RwLock::new(Vec::new());

-#[cfg(debug_assertions)]
+#[cfg(feature = "testing")]
 pub fn add_gasless_token_for_testing(type_string: String, min_transfer: u64) {
     GASLESS_TOKENS_FOR_TESTING
         .write()
@@ -981,7 +981,7 @@ pub fn add_gasless_token_for_testing(type_string: String, min_transfer: u64) {
         .push((type_string, min_transfer));
 }

-#[cfg(debug_assertions)]
+#[cfg(feature = "testing")]
 pub fn clear_gasless_tokens_for_testing() {
     GASLESS_TOKENS_FOR_TESTING.write().unwrap().clear();
 }
@@ -1120,10 +1120,8 @@ pub fn get_gasless_allowed_token_types(config: &ProtocolConfig) -> Arc<BTreeMap<
     apply_test_token_overrides(arc)
 }

-/// Merges debug-only token overrides into the cached map.
-/// In release builds this is a no-op that returns the input unchanged.
 fn apply_test_token_overrides(base: Arc<BTreeMap<TypeTag, u64>>) -> Arc<BTreeMap<TypeTag, u64>> {
-    #[cfg(debug_assertions)]
+    #[cfg(feature = "testing")]
     {
         let overrides = GASLESS_TOKENS_FOR_TESTING.read().unwrap();
         if !overrides.is_empty() {
@@ -1134,6 +1132,8 @@ fn apply_test_token_overrides(base: Arc<BTreeMap<TypeTag, u64>>) -> Arc<BTreeMap<
         }
     }

+    // In non-testing builds, this function is a no-op that returns the input unchanged.
+    // The #[cfg(feature = "testing")] block above is compiled only when the feature is enabled.
     base
 }

diff --git a/crates/sui-verifier-transactional-tests/Cargo.toml b/crates/sui-verifier-transactional-tests/Cargo.toml
index e5146a67d168a..376debefb0f11 100644
--- a/crates/sui-verifier-transactional-tests/Cargo.toml
+++ b/crates/sui-verifier-transactional-tests/Cargo.toml
@@ -9,7 +9,7 @@ edition = "2024"

 [dev-dependencies]
 datatest-stable.workspace = true
-sui-transactional-test-runner.workspace = true
+sui-transactional-test-runner = { workspace = true, features = ["testing"] }

 [[test]]
 name = "tests"
PATCH

echo "Patch applied successfully"
