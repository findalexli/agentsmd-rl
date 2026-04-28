#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Uploads multiple vector-embedded points to a Qdrant collection using the Python " "skills/qdrant-clients-sdk/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-clients-sdk/SKILL.md b/skills/qdrant-clients-sdk/SKILL.md
@@ -29,17 +29,46 @@ prototype.
 
 ## Code examples
 
-<!-- ToDo: make it work -->
-
 To obtain code examples for a specific client and use-case, you can make a search request to library of curated code snippets for Qdrant client.
 
 ```bash
-curl -X GET "https://snippets.qdrant.tech/search?client=python&query=how+to+upsert+vectors"
+curl -X GET "https://snippets.qdrant.tech/search?language=python&query=how+to+upload+points"
 ```
 
+Available languages: `python`, `typescript`, `rust`, `java`, `go`, `csharp`
+
+
 Response example:
 
-```json
-TODO
+```markdown
+
+## Snippet 1
+
+*qdrant-client* (vlatest) — https://qdrant.tech/documentation/concepts/points/
+
+Uploads multiple vector-embedded points to a Qdrant collection using the Python qdrant_client (PointStruct) with id, payload (e.g., color), and a 3D-like vector for similarity search. It supports parallel uploads (parallel=4) and a retry policy (max_retries=3) for robust indexing. The operation is idempotent: re-uploading with the same id overwrites existing points; if ids aren’t provided, Qdrant auto-generates UUIDs.
+
+client.upload_points(
+    collection_name="{collection_name}",
+    points=[
+        models.PointStruct(
+            id=1,
+            payload={
+                "color": "red",
+            },
+            vector=[0.9, 0.1, 0.1],
+        ),
+        models.PointStruct(
+            id=2,
+            payload={
+                "color": "green",
+            },
+            vector=[0.1, 0.9, 0.1],
+        ),
+    ],
+    parallel=4,
+    max_retries=3,
+)
 ```
 
+If snippet output is required in json format, you can add `&format=json` to the query string
PATCH

echo "Gold patch applied."
