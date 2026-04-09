#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch to implement feature flag gating for coin reservation obj refs
patch -p1 <<'PATCH'
diff --git a/crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs b/crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs
index 1987ab726e4a6..869a07b8ea47d 100644
--- a/crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs
+++ b/crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs
@@ -33,6 +33,10 @@ pub(crate) async fn load_address_balance_coin(
         return Ok(None);
     }

+    if !super::latest_feature_flag(ctx, "enable_coin_reservation_obj_refs").await? {
+        return Ok(None);
+    }
+
     let balance_type = Balance::type_tag(coin_type.clone());
     let accumulator_id = AccumulatorValue::get_field_id(owner, &balance_type)
         .context("Failed to derive accumulator field ID")?;
@@ -44,7 +48,7 @@ pub(crate) async fn load_address_balance_coin(

     let accumulator_version = accumulator_obj.version();
     let previous_transaction = accumulator_obj.previous_transaction;
-    let epoch = super::current_epoch(ctx).await?;
+    let epoch = super::latest_epoch(ctx).await?;
     let chain_identifier = ctx
         .chain_identifier()
         .context("Chain identifier not available (no database configured)")?;
diff --git a/crates/sui-indexer-alt-jsonrpc/src/data/mod.rs b/crates/sui-indexer-alt-jsonrpc/src/data/mod.rs
index f824f44d17fdd..887b3d038cb9c 100644
--- a/crates/sui-indexer-alt-jsonrpc/src/data/mod.rs
+++ b/crates/sui-indexer-alt-jsonrpc/src/data/mod.rs
@@ -3,34 +3,11 @@

 mod address_balance_coins;
 mod object;
-
-use anyhow::Context as _;
-use diesel::ExpressionMethods;
-use diesel::QueryDsl;
-use sui_indexer_alt_schema::schema::kv_epoch_starts;
-use sui_types::committee::EpochId;
-
-use crate::context::Context;
+mod system_state;

 pub(crate) use address_balance_coins::load_address_balance_coin;
 pub(crate) use address_balance_coins::try_resolve_address_balance_object;
 pub(crate) use object::load_live;
 pub(crate) use object::load_live_deserialized;
-
-/// Query the latest epoch from the database.
-pub(crate) async fn current_epoch(ctx: &Context) -> Result<EpochId, anyhow::Error> {
-    use kv_epoch_starts::dsl as e;
-
-    let mut conn = ctx
-        .pg_reader()
-        .connect()
-        .await
-        .context("Failed to connect to the database")?;
-
-    let epoch: i64 = conn
-        .first(e::kv_epoch_starts.select(e::epoch).order(e::epoch.desc()))
-        .await
-        .context("Failed to fetch the current epoch")?;
-
-    Ok(epoch as EpochId)
-}
+pub(crate) use system_state::latest_epoch;
+pub(crate) use system_state::latest_feature_flag;
diff --git a/crates/sui-indexer-alt-jsonrpc/src/data/system_state.rs b/crates/sui-indexer-alt-jsonrpc/src/data/system_state.rs
new file mode 100644
index 0000000000000..5a2380f28d533
--- /dev/null
+++ b/crates/sui-indexer-alt-jsonrpc/src/data/system_state.rs
@@ -0,0 +1,56 @@
+// Copyright (c) Mysten Labs, Inc.
+// SPDX-License-Identifier: Apache-2.0
+
+use anyhow::Context as _;
+use diesel::ExpressionMethods;
+use diesel::QueryDsl;
+use sui_indexer_alt_schema::schema::kv_epoch_starts;
+use sui_indexer_alt_schema::schema::kv_feature_flags;
+use sui_types::committee::EpochId;
+
+use crate::context::Context;
+
+/// Query the latest epoch from the database.
+pub(crate) async fn latest_epoch(ctx: &Context) -> Result<EpochId, anyhow::Error> {
+    use kv_epoch_starts::dsl as e;
+
+    let mut conn = ctx
+        .pg_reader()
+        .connect()
+        .await
+        .context("Failed to connect to the database")?;
+
+    let epoch: i64 = conn
+        .first(e::kv_epoch_starts.select(e::epoch).order(e::epoch.desc()))
+        .await
+        .context("Failed to fetch the current epoch")?;
+
+    Ok(epoch as EpochId)
+}
+
+/// Query the latest value for a given feature flag, from the database.
+pub(crate) async fn latest_feature_flag(ctx: &Context, name: &str) -> Result<bool, anyhow::Error> {
+    use kv_feature_flags::dsl as f;
+
+    let mut conn = ctx
+        .pg_reader()
+        .connect()
+        .await
+        .context("Failed to connect to the database")?;
+
+    let query = f::kv_feature_flags
+        .select(f::flag_value)
+        .filter(f::flag_name.eq(name))
+        .order(f::protocol_version.desc())
+        .limit(1);
+
+    let flag: bool = conn
+        .results(query)
+        .await
+        .with_context(|| format!("Failed to fetch latest flag value for '{}'", name))?
+        .first()
+        .copied()
+        .unwrap_or(false);
+
+    Ok(flag)
+}
PATCH

# Verify the distinctive line was added
grep -q "enable_coin_reservation_obj_refs" crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs || {
    echo "ERROR: Feature flag check not found in address_balance_coins.rs"
    exit 1
}

echo "Patch applied successfully"
