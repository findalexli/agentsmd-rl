#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "enable_coin_reservation_obj_refs()" crates/sui-json-rpc/src/authority_state.rs; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply
diff --git a/crates/sui-e2e-tests/tests/address_balance_rpc_tests.rs b/crates/sui-e2e-tests/tests/address_balance_rpc_tests.rs
index e509911bd603..237c81db41bc 100644
--- a/crates/sui-e2e-tests/tests/address_balance_rpc_tests.rs
+++ b/crates/sui-e2e-tests/tests/address_balance_rpc_tests.rs
@@ -11,6 +11,7 @@ use sui_json_rpc_types::{
     Balance as RpcBalance, CoinPage, SuiData, SuiObjectDataOptions, SuiObjectResponse,
 };
 use sui_macros::*;
+use sui_types::error::SuiObjectResponseError;
 use sui_types::{
     base_types::{ObjectID, SuiAddress},
     coin_reservation::ParsedDigest,
@@ -687,3 +688,80 @@ async fn test_get_balance_includes_address_balance() {
         );
     }
 }
+
+#[sim_test]
+async fn test_no_fake_coins_when_coin_reservations_disabled() {
+    // Enable address balances but explicitly disable coin reservations.
+    // Verify that getCoins does not return fake coins.
+    let mut test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.enable_address_balance_gas_payments_for_testing();
+            cfg.disable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let (sender, _) = test_env.get_sender_and_gas(0);
+    test_env
+        .fund_one_address_balance(sender, 1_000_000_000)
+        .await;
+
+    let counts = get_coins_counts(&test_env, sender, None).await;
+    assert_eq!(
+        counts.fake_coins, 0,
+        "No fake coins should be returned when coin reservations are disabled"
+    );
+
+    let all_counts = get_all_coins_counts(&test_env, sender).await;
+    assert_eq!(
+        all_counts.fake_coins, 0,
+        "getAllCoins should not return fake coins when coin reservations are disabled"
+    );
+}
+
+#[sim_test]
+async fn test_get_object_no_fake_coin_when_coin_reservations_disabled() {
+    // Enable address balances but explicitly disable coin reservations.
+    // Verify that sui_getObject does not return a fake coin for a masked object ID.
+    let mut test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.enable_address_balance_gas_payments_for_testing();
+            cfg.disable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let (sender, _) = test_env.get_sender_and_gas(0);
+    let amount = 1_000_000_000u64;
+    test_env.fund_one_address_balance(sender, amount).await;
+
+    // Create a masked object ID as if coin reservations were enabled.
+    let fake_coin_ref = test_env.encode_coin_reservation(sender, 0, amount);
+    let masked_object_id = fake_coin_ref.0;
+
+    let params = rpc_params![
+        masked_object_id,
+        SuiObjectDataOptions::new().with_content().with_owner()
+    ];
+    let response: SuiObjectResponse = test_env
+        .cluster
+        .fullnode_handle
+        .rpc_client
+        .request("sui_getObject", params)
+        .await
+        .unwrap();
+
+    assert!(
+        response.data.is_none(),
+        "sui_getObject should not return a fake coin when coin reservations are disabled"
+    );
+    assert!(
+        matches!(
+            response.error,
+            Some(SuiObjectResponseError::NotExists { .. })
+        ),
+        "Expected NotExists error for masked object ID when coin reservations disabled"
+    );
+}
diff --git a/crates/sui-json-rpc/src/authority_state.rs b/crates/sui-json-rpc/src/authority_state.rs
index d265346df336..525d71e4ba57 100644
--- a/crates/sui-json-rpc/src/authority_state.rs
+++ b/crates/sui-json-rpc/src/authority_state.rs
@@ -251,8 +251,14 @@ impl StateRead for AuthorityState {
     fn get_object_read(&self, object_id: &ObjectID) -> StateReadResult<ObjectRead> {
         let result = self.get_object_read(object_id)?;

-        // If object not found, check if this is a masked object ID (fake coin request).
-        if let ObjectRead::NotExists(object_id) = result {
+        // If object not found and coin reservations are enabled, check if this is a
+        // masked object ID (fake coin request).
+        if let ObjectRead::NotExists(object_id) = result
+            && self
+                .load_epoch_store_one_call_per_task()
+                .protocol_config()
+                .enable_coin_reservation_obj_refs()
+        {
             let chain_identifier = self.get_chain_identifier();
             let unmasked_id = coin_reservation::mask_or_unmask_id(object_id, chain_identifier);

@@ -501,8 +507,15 @@ impl StateRead for AuthorityState {
             }
         }

-        // Build fake coins map.
-        let fake_coins: HashMap<String, SuiCoin> = if one_coin_type_only {
+        // Build fake coins map (only when coin reservations are enabled).
+        let coin_reservations_enabled = self
+            .load_epoch_store_one_call_per_task()
+            .protocol_config()
+            .enable_coin_reservation_obj_refs();
+
+        let fake_coins: HashMap<String, SuiCoin> = if !coin_reservations_enabled {
+            HashMap::new()
+        } else if one_coin_type_only {
             let balance_type_tag = sui_types::parse_sui_type_tag(&cursor.0)
                 .map_err(|e| anyhow::anyhow!("Invalid coin type: {} - {}", cursor.0, e))?;
             let balance_type = Balance::type_tag(balance_type_tag);
PATCH

echo "Patch applied successfully"
