#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch to fix the timings crash
patch -p1 << 'EOF'
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
EOF

# Idempotency check - verify the distinctive warning log line exists
grep -q "execution produced more timings than the original PTB commands" crates/sui-core/src/authority/execution_time_estimator.rs || {
    echo "ERROR: Patch not applied correctly"
    exit 1
}

echo "Gold patch applied successfully"
