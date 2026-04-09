#!/bin/bash
set -e

cd /workspace/chroma

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/rust/chroma/src/collection.rs b/rust/chroma/src/collection.rs
index c94af3e478a..61d913a9f8c 100644
--- a/rust/chroma/src/collection.rs
+++ b/rust/chroma/src/collection.rs
@@ -182,7 +182,7 @@ impl ChromaCollection {
     /// # Example
     ///
     /// ```
-    /// use chroma_types::plan::ReadLevel;
+    /// use chroma::types::ReadLevel;
     ///
     /// # async fn example(collection: &chroma::ChromaCollection) -> Result<(), Box<dyn std::error::Error>> {
     /// // Skip WAL for faster count (may miss recent writes)
@@ -576,7 +576,7 @@ impl ChromaCollection {
     /// # Example
     ///
     /// ```
-    /// use chroma_types::plan::{SearchPayload, ReadLevel};
+    /// use chroma::types::{SearchPayload, ReadLevel};
     ///
     /// # async fn example(collection: &chroma::ChromaCollection) -> Result<(), Box<dyn std::error::Error>> {
     /// let search = SearchPayload::default().limit(Some(10), 0);
diff --git a/rust/chroma/src/types.rs b/rust/chroma/src/types.rs
index 82b8a1ff7f1..254386159a8 100644
--- a/rust/chroma/src/types.rs
+++ b/rust/chroma/src/types.rs
@@ -13,6 +13,7 @@ pub use chroma_types::operator::QueryVector;
 pub use chroma_types::operator::Rank;
 pub use chroma_types::operator::RankExpr;
 pub use chroma_types::operator::Select;
+pub use chroma_types::plan::ReadLevel;
 pub use chroma_types::plan::SearchPayload;
 pub use chroma_types::regex::hir::ChromaHir;
 pub use chroma_types::regex::ChromaRegex;
PATCH

# Verify the patch was applied
if ! grep -q "pub use chroma_types::plan::ReadLevel;" rust/chroma/src/types.rs; then
    echo "ERROR: Patch failed to apply - ReadLevel re-export not found"
    exit 1
fi

echo "Patch applied successfully"
