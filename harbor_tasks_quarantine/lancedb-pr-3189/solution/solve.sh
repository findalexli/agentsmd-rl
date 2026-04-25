#!/bin/bash
set -e

# Navigate to the repo
cd /workspace/lancedb

# Apply the gold patch for PR #3189: fix raise instead of return ValueError
cat <<'PATCH' | git apply -
diff --git a/python/python/lancedb/query.py b/python/python/lancedb/query.py
index 123456..789abc 100644
--- a/python/python/lancedb/query.py
+++ b/python/python/lancedb/query.py
@@ -70,7 +70,7 @@ def ensure_vector_query(
 ) -> Union[List[float], List[List[float]], pa.Array, List[pa.Array]]:
     if isinstance(val, list):
         if len(val) == 0:
-            return ValueError("Vector query must be a non-empty list")
+            raise ValueError("Vector query must be a non-empty list")
         sample = val[0]
     else:
         if isinstance(val, float):
@@ -83,7 +83,7 @@ def ensure_vector_query(
         return val
     if isinstance(sample, list):
         if len(sample) == 0:
-            return ValueError("Vector query must be a non-empty list")
+            raise ValueError("Vector query must be a non-empty list")
         if isinstance(sample[0], float):
             # val is list of list of floats
             return val
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q 'raise ValueError("Vector query must be a non-empty list")' python/python/lancedb/query.py || {
    echo "ERROR: Patch was not applied successfully"
    exit 1
}

echo "Gold patch applied successfully"
