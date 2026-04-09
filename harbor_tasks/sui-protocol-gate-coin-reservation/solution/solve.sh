#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for PR #26088
cat <<'PATCH' | git apply -
diff --git a/crates/sui-core/src/authority.rs b/crates/sui-core/src/authority.rs
index bef0438a08d9..2d7a761acca4 100644
--- a/crates/sui-core/src/authority.rs
+++ b/crates/sui-core/src/authority.rs
@@ -2497,6 +2497,22 @@ impl AuthorityState {
             .into());
         }

+        // Reject coin reservations in gas payment when the execution engine
+        // doesn't support them.
+        let protocol_config = epoch_store.protocol_config();
+        if !protocol_config.enable_coin_reservation_obj_refs()
+            && transaction.gas().iter().any(|obj_ref| {
+                sui_types::coin_reservation::ParsedDigest::is_coin_reservation_digest(&obj_ref.2)
+            })
+        {
+            return Err(SuiErrorKind::UnsupportedFeatureError {
+                error:
+                    "coin reservations in gas payment are not supported at this protocol version"
+                        .to_string(),
+            }
+            .into());
+        }
+
         // Cheap validity checks for a transaction, including input size limits.
         transaction.validity_check_no_gas_check(epoch_store.protocol_config())?;

diff --git a/crates/sui-e2e-tests/tests/grpc_simulate_gas_coin_tests.rs b/crates/sui-e2e-tests/tests/grpc_simulate_gas_coin_tests.rs
index 4917d4e1ce17..cc6bf5d5b536 100644
--- a/crates/sui-e2e-tests/tests/grpc_simulate_gas_coin_tests.rs
+++ b/crates/sui-e2e-tests/tests/grpc_simulate_gas_coin_tests.rs
@@ -128,11 +128,25 @@ async fn test_has_ab_has_coins_uses_gas_coin() {

     // First element should be a coin reservation (identified by magic in digest)
     let first_payment = &gas_payment[0];
-    assert!(
-        ParsedDigest::is_coin_reservation_digest(&first_payment.2),
-        "First gas payment should be a coin reservation, got digest: {:?}",
-        first_payment.2
-    );
+
+    // Coin reservation is not enabled on mainnet yet, so if the override is enabled we should NOT
+    // see a coin reservation digest.
+    if sui_simulator::has_mainnet_protocol_config_override() {
+        // Assert this here so that when it gets enabled in mainnet this will fail so you know to
+        // remove the override check and update the test expectations here.
+        assert!(
+            !ParsedDigest::is_coin_reservation_digest(&first_payment.2),
+            "Mainnet override should disable coin reservation, got digest: {:?}",
+            first_payment.2
+        );
+        return; // Skip the rest of the test since the mainnet override disables coin reservation
+    } else {
+        assert!(
+            ParsedDigest::is_coin_reservation_digest(&first_payment.2),
+            "First gas payment should be a coin reservation, got digest: {:?}",
+            first_payment.2
+        );
+    }

     // Verify the entire address balance is reserved, not just the gas budget
     // Note: The actual balance may be slightly less than ab_amount due to gas
@@ -693,11 +707,23 @@ async fn test_combined_ab_and_coins_needed() {
     );

     let response = result.unwrap();
-    assert!(
-        response.transaction.effects.status().is_ok(),
-        "Expected successful execution with combined funds, got: {:?}",
-        response.transaction.effects.status()
-    );
+
+    // Not enabled on mainnet yet, so mainnet override should still fail as the overrides above
+    // aren't applied to the RPC.
+    if sui_simulator::has_mainnet_protocol_config_override() {
+        assert!(
+            response.transaction.effects.status().is_err(),
+            "Expected execution to fail due to insufficient funds with mainnet override, got: {:?}",
+            response.transaction.effects.status()
+        );
+        return; // Skip the rest of the test since the mainnet override disables coin reservation
+    } else {
+        assert!(
+            response.transaction.effects.status().is_ok(),
+            "Expected successful execution with combined funds, got: {:?}",
+            response.transaction.effects.status()
+        );
+    }

     // Verify coin reservation is used to combine both sources
     let gas_payment = response.transaction.transaction.gas_data().payment.clone();
diff --git a/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs b/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs
index 12d4c21cd70a..2db3a9a392f7 100644
--- a/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs
+++ b/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs
@@ -145,11 +145,7 @@ pub fn simulate_transaction(
         }

         if transaction.gas_data().payment.is_empty() {
-            select_gas(
-                service,
-                &mut transaction,
-                protocol_config.max_gas_payment_objects(),
-            )?;
+            select_gas(service, &mut transaction, &protocol_config)?;
         }
     }

@@ -364,7 +360,7 @@ fn round_up_to_nearest(value: u64, step: u64) -> u64 {
 fn select_gas(
     service: &RpcService,
     transaction: &mut sui_types::transaction::TransactionData,
-    max_gas_payment_objects: u32,
+    protocol_config: &ProtocolConfig,
 ) -> Result<()> {
     use sui_types::accumulator_root::AccumulatorValue;
     use sui_types::balance::Balance;
@@ -459,7 +455,7 @@ fn select_gas(
                     .ok()
                     .map(|coin| (object.compute_object_reference(), coin.value()))
             })
-            .take(max_gas_payment_objects as usize);
+            .take(protocol_config.max_gas_payment_objects() as usize);

         let mut selected_gas = vec![];
         let mut selected_gas_value = 0;
@@ -473,7 +469,8 @@ fn select_gas(

         // When GasCoin is used and there's address balance, prepend a coin reservation
         // to make all SUI in the account available (coins + address balance)
-        if gas_coin_used
+        if protocol_config.enable_coin_reservation_obj_refs()
+            && gas_coin_used
             && let Some(ab_value) = address_balance
             && ab_value > 0
         {
PATCH

# Verify the patch was applied by checking for a distinctive line
grep -q "coin reservations in gas payment are not supported at this protocol version" crates/sui-core/src/authority.rs && echo "Patch applied successfully"
