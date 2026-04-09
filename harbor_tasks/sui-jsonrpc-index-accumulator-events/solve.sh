#!/bin/bash
set -e

cd /workspace/sui

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/crates/sui-core/src/jsonrpc_index.rs b/crates/sui-core/src/jsonrpc_index.rs
index c44ae5912281..c6deb8a29b31 100644
--- a/crates/sui-core/src/jsonrpc_index.rs
+++ b/crates/sui-core/src/jsonrpc_index.rs
@@ -1112,15 +1112,20 @@ impl IndexStore {
                 .map(|(obj_id, module, function)| ((obj_id, module, function, sequence), *digest)),
         )?;

-        batch.insert_batch(
-            &self.tables.transactions_to_addr,
-            mutated_objects.filter_map(|(_, owner)| {
+        // objects sent to addresses and accumulator events
+        let affected_addresses = mutated_objects
+            .filter_map(|(_, owner)| {
                 owner
                     .get_address_owner_address()
                     .ok()
                     .map(|addr| ((addr, sequence), digest))
-            }),
-        )?;
+            })
+            .chain(
+                accumulator_events
+                    .iter()
+                    .map(|event| ((event.write.address.address, sequence), digest)),
+            );
+        batch.insert_batch(&self.tables.transactions_to_addr, affected_addresses)?;

         // Coin Index
         let cache_updates = self.index_coin(
PATCH

echo "Patch applied successfully"
