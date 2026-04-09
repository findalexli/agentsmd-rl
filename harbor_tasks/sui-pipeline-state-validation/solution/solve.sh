#!/bin/bash
set -euo pipefail

cd /workspace/sui

# Apply the gold patch from PR #26022
cat <<'PATCH' | git apply -
diff --git a/crates/sui-indexer-alt-framework/src/pipeline/mod.rs b/crates/sui-indexer-alt-framework/src/pipeline/mod.rs
index 3771ea915e3f6..4d04bb8e0b278 100644
--- a/crates/sui-indexer-alt-framework/src/pipeline/mod.rs
+++ b/crates/sui-indexer-alt-framework/src/pipeline/mod.rs
@@ -123,13 +123,19 @@ impl WatermarkPart {

     /// Add the rows from `other` to this part.
     fn add(&mut self, other: WatermarkPart) {
-        debug_assert_eq!(self.checkpoint(), other.checkpoint());
+        assert_eq!(self.checkpoint(), other.checkpoint());
         self.batch_rows += other.batch_rows;
+        assert!(
+            self.batch_rows <= self.total_rows,
+            "batch_rows ({}) exceeded total_rows ({})",
+            self.batch_rows,
+            self.total_rows,
+        );
     }

     /// Record that `rows` have been taken from this part.
     fn take(&mut self, rows: usize) -> WatermarkPart {
-        debug_assert!(
+        assert!(
             self.batch_rows >= rows,
             "Can't take more rows than are available"
         );
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q 'batch_rows ({}) exceeded total_rows ({})' crates/sui-indexer-alt-framework/src/pipeline/mod.rs

# Add regression tests to the test module
cat <<'TEST_PATCH' | git apply -
--- a/crates/sui-indexer-alt-framework/src/pipeline/mod.rs
+++ b/crates/sui-indexer-alt-framework/src/pipeline/mod.rs
@@ -235,4 +235,51 @@ mod tests {

         assert_eq!(checkpoint.len(), 0);
         assert_eq!(checkpoint.checkpoint(), 100);
     }
+
+    #[test]
+    #[should_panic(expected = "batch_rows")]
+    fn test_watermark_part_batch_rows_exceeds_total() {
+        let mut part = WatermarkPart {
+            watermark: CommitterWatermark::default(),
+            batch_rows: 150,
+            total_rows: 200,
+        };
+
+        // Adding this should cause batch_rows (150+100=250) to exceed total_rows (200)
+        part.add(WatermarkPart {
+            watermark: CommitterWatermark::default(),
+            batch_rows: 100,
+            total_rows: 200,
+        });
+    }
+
+    #[test]
+    #[should_panic(expected = "Can't take more rows")]
+    fn test_watermark_part_take_too_many() {
+        let mut part = WatermarkPart {
+            watermark: CommitterWatermark::default(),
+            batch_rows: 50,
+            total_rows: 200,
+        };
+
+        // Trying to take more than available should panic
+        let _ = part.take(100);
+    }
+
+    #[test]
+    #[should_panic(expected = "checkpoint")]
+    fn test_watermark_part_checkpoint_mismatch() {
+        let mut part1 = WatermarkPart {
+            watermark: CommitterWatermark { checkpoint_hi_inclusive: 100, ..Default::default() },
+            batch_rows: 50,
+            total_rows: 200,
+        };
+
+        let part2 = WatermarkPart {
+            watermark: CommitterWatermark { checkpoint_hi_inclusive: 200, ..Default::default() },
+            batch_rows: 50,
+            total_rows: 200,
+        };
+
+        // Adding parts with different checkpoints should panic
+        part1.add(part2);
+    }
 }
TEST_PATCH

echo "Patch applied successfully"
