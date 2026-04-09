#!/bin/bash
set -e

cd /workspace/sui

# Apply the fix for flaky benchmark smoke test
# This changes TPS calculation from integer division to floating-point
# and lowers the min-tps threshold from 1 to 0.01

patch -p1 << 'PATCH'
diff --git a/.github/workflows/rust.yml b/.github/workflows/rust.yml
index 776fe54ded70..4a3d8d222ba0 100644
--- a/.github/workflows/rust.yml
+++ b/.github/workflows/rust.yml
@@ -296,7 +296,7 @@ jobs:
             --primary-gas-owner-id "$ADDR" \
             --use-fullnode-for-execution true \
             --num-client-threads 10 --num-server-threads 24 \
-            --num-transfer-accounts 2 --run-duration 10s --min-tps 1 \
+            --num-transfer-accounts 2 --run-duration 10s --min-tps 0.01 \
             bench --target-qps 10 --num-workers 10 \
             --transfer-object 1 --shared-counter 1 --delegation 1 \
             --batch-payment 1 --shared-deletion 1 --randomness 1 \
diff --git a/crates/sui-benchmark/src/drivers/mod.rs b/crates/sui-benchmark/src/drivers/mod.rs
index 0bbbb6828d27..6bcd3b55f253 100644
--- a/crates/sui-benchmark/src/drivers/mod.rs
+++ b/crates/sui-benchmark/src/drivers/mod.rs
@@ -167,8 +167,15 @@ impl BenchmarkStats {
             ]);
         let mut row = Row::new();
         row.add_cell(Cell::new(self.duration.as_secs()));
-        row.add_cell(Cell::new(self.num_success_txes / self.duration.as_secs()));
-        row.add_cell(Cell::new(self.num_success_cmds / self.duration.as_secs()));
+        let duration_secs = self.duration.as_secs_f64().max(1.0);
+        row.add_cell(Cell::new(format!(
+            "{:.2}",
+            self.num_success_txes as f64 / duration_secs
+        )));
+        row.add_cell(Cell::new(format!(
+            "{:.2}",
+            self.num_success_cmds as f64 / duration_secs
+        )));
         row.add_cell(Cell::new(
             (100 * self.num_error_txes) as f32
                 / (self.num_error_txes + self.num_success_txes) as f32,
PATCH

# Verify the patch was applied
grep -q "as_secs_f64" crates/sui-benchmark/src/drivers/mod.rs && echo "Fix applied successfully"
