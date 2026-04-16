#!/bin/bash
set -e

cd /workspace/lancedb

# Apply the gold patch for PR #3030: fix empty hybrid search handling
cat <<'PATCH' | git apply -
diff --git a/python/python/lancedb/query.py b/python/python/lancedb/query.py
index 926b515275..01f8328f7c 100644
--- a/python/python/lancedb/query.py
+++ b/python/python/lancedb/query.py
@@ -1782,6 +1782,26 @@ def _combine_hybrid_results(
             vector_results = LanceHybridQueryBuilder._rank(vector_results, "_distance")
             fts_results = LanceHybridQueryBuilder._rank(fts_results, "_score")

+        # If both result sets are empty (e.g. after hard filtering),
+        # return early to avoid errors in reranking or score restoration.
+        if vector_results.num_rows == 0 and fts_results.num_rows == 0:
+            # Build a minimal empty table with the _relevance_score column
+            combined_schema = pa.unify_schemas(
+                [vector_results.schema, fts_results.schema],
+            )
+            empty = pa.table(
+                {
+                    col: pa.array([], type=combined_schema.field(col).type)
+                    for col in combined_schema.names
+                }
+            )
+            empty = empty.append_column(
+                "_relevance_score", pa.array([], type=pa.float32())
+            )
+            if not with_row_ids and "_rowid" in empty.column_names:
+                empty = empty.drop(["_rowid"])
+            return empty
+
         original_distances = None
         original_scores = None
         original_distance_row_ids = None
PATCH

echo "Patch applied successfully"
