#!/bin/bash
set -e

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

# Idempotency check - verify the patch was applied
grep -q 'batch_rows ({}) exceeded total_rows ({})' crates/sui-indexer-alt-framework/src/pipeline/mod.rs
echo "Patch applied successfully"
