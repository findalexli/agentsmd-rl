#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

if grep -q "/data/batch" areal/infra/rpc/rpc_server.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/infra/rpc/rpc_server.py b/areal/infra/rpc/rpc_server.py
index 5e2a261c4..a9b03ec37 100644
--- a/areal/infra/rpc/rpc_server.py
+++ b/areal/infra/rpc/rpc_server.py
@@ -845,6 +845,60 @@ def retrieve_batch_data(shard_id: str):
         return jsonify({"status": "error", "message": str(e)}), 500
 
 
+@app.route("/data/batch", methods=["POST"])
+def retrieve_batch_data_many():
+    """Retrieve multiple batch data shards in one request."""
+
+    try:
+        payload = request.get_json(silent=True) or {}
+        shard_ids = payload.get("shard_ids", [])
+        if not isinstance(shard_ids, list) or not all(
+            isinstance(shard_id, str) for shard_id in shard_ids
+        ):
+            return (
+                jsonify(
+                    {
+                        "status": "error",
+                        "message": "Expected JSON body with string list field 'shard_ids'",
+                    }
+                ),
+                400,
+            )
+
+        data = []
+        missing_shard_ids = []
+        for shard_id in shard_ids:
+            try:
+                data.append(rtensor.fetch(shard_id))
+            except KeyError:
+                missing_shard_ids.append(shard_id)
+
+        if missing_shard_ids:
+            return (
+                jsonify(
+                    {
+                        "status": "error",
+                        "message": "One or more requested shards were not found",
+                        "missing_shard_ids": missing_shard_ids,
+                    }
+                ),
+                400,
+            )
+
+        serialized_data = serialize_value(data)
+        data_bytes = orjson.dumps(serialized_data)
+        logger.debug(
+            "Retrieved %s batch shards (size=%s bytes)",
+            len(shard_ids),
+            len(data_bytes),
+        )
+        return Response(data_bytes, mimetype="application/octet-stream")
+
+    except Exception as e:
+        logger.error(f"Error retrieving batch shards: {e}\n{traceback.format_exc()}")
+        return jsonify({"status": "error", "message": str(e)}), 500
+
+
 @app.route("/data/clear", methods=["DELETE"])
 def clear_batch_data():
     """Clear specified batch data shards.
PATCH
