#!/bin/bash
set -e

cd /workspace/sui

# Apply the fix patch
bash -c 'cat > /tmp/fix.patch << '"'"'PATCH'"'"'
diff --git a/crates/sui-core/src/authority/execution_time_estimator.rs b/crates/sui-core/src/authority/execution_time_estimator.rs
index 6793e35b43fe..0f3882644b62 100644
--- a/crates/sui-core/src/authority/execution_time_estimator.rs
+++ b/crates/sui-core/src/authority/execution_time_estimator.rs
@@ -316,12 +316,20 @@ impl ExecutionTimeObserver {
         total_duration: Duration,
         gas_price: u64,
     ) {
-        assert!(tx.commands.len() >= timings.len());
-
         let Some(epoch_store) = self.epoch_store.upgrade() else {
             debug!("epoch is ending, dropping execution time observation");
             return;
         };
+        let timings = if timings.len() > tx.commands.len() {
+            warn!(
+                executed_commands = timings.len(),
+                original_commands = tx.commands.len(),
+                "execution produced more timings than the original PTB commands; using the trailing timings for local execution-time observations"
+            );
+            &timings[timings.len() - tx.commands.len()..]
+        } else {
+            timings
+        };

         let mut uses_indebted_object = false;

PATCH'

# Apply the patch
git apply /tmp/fix.patch

# Idempotency check: verify the distinctive line is present
grep -q "execution produced more timings than the original PTB commands" crates/sui-core/src/authority/execution_time_estimator.rs || exit 1

echo "Fix applied successfully"
