#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched (idempotency check)
if grep -q "is_gasless =" crates/sui-core/src/authority.rs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch for gasless transaction fix
patch -p1 << 'PATCH'
diff --git a/crates/sui-core/src/authority.rs b/crates/sui-core/src/authority.rs
index eb924520f1c..18b942a60ac 100644
--- a/crates/sui-core/src/authority.rs
+++ b/crates/sui-core/src/authority.rs
@@ -2305,7 +2305,23 @@ impl AuthorityState {

         // make a gas object if one was not provided
         let mut gas_data = transaction.gas_data().clone();
-        let ((gas_status, checked_input_objects), mock_gas) = if transaction.gas().is_empty() {
+        let is_gasless =
+            epoch_store.protocol_config().enable_gasless() && transaction.is_gasless_transaction();
+        let ((gas_status, checked_input_objects), mock_gas) = if is_gasless {
+            // Gasless transactions don't use gas coins — skip mock gas object injection.
+            (
+                sui_transaction_checks::check_transaction_input(
+                    epoch_store.protocol_config(),
+                    epoch_store.reference_gas_price(),
+                    &transaction,
+                    input_objects,
+                    &receiving_objects,
+                    &self.metrics.bytecode_verifier_metrics,
+                    &self.config.verifier_signing_config,
+                )?,
+                None,
+            )
+        } else if transaction.gas().is_empty() {
             let sender = transaction.sender();
             // use a 1B sui coin
             const MIST_TO_SUI: u64 = 1_000_000_000;
@@ -2526,7 +2542,10 @@ impl AuthorityState {
         // Create and inject mock gas coin before pre_object_load_checks so that
         // funds withdrawal processing sees non-empty payment and doesn't incorrectly
         // create an address balance withdrawal for gas.
-        let mock_gas_object = if allow_mock_gas_coin && transaction.gas().is_empty() {
+        // Skip mock gas for gasless transactions — they don't use gas coins.
+        let is_gasless = protocol_config.enable_gasless() && transaction.is_gasless_transaction();
+        let mock_gas_object = if allow_mock_gas_coin && transaction.gas().is_empty() && !is_gasless
+        {
             let obj = Object::new_move(
                 MoveObject::new_gas_coin(
                     OBJECT_START_VERSION,
PATCH

echo "Patch applied successfully!"
