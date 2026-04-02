#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency check: skip if batch endpoint already exists
if grep -q 'async def retrieve_data_shard_batch' areal/experimental/inference_service/data_proxy/app.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/experimental/inference_service/data_proxy/app.py b/areal/experimental/inference_service/data_proxy/app.py
index 04832d5ed..1c2a1402d 100644
--- a/areal/experimental/inference_service/data_proxy/app.py
+++ b/areal/experimental/inference_service/data_proxy/app.py
@@ -6,8 +6,8 @@

 import orjson
 from fastapi import FastAPI, HTTPException, Request
+from fastapi.responses import JSONResponse, StreamingResponse
 from fastapi.responses import Response as RawResponse
-from fastapi.responses import StreamingResponse
 from openai.types.chat.completion_create_params import CompletionCreateParams
 from pydantic import BaseModel

@@ -384,6 +384,68 @@ async def export_trajectories(
     # via HttpRTensorBackend._fetch_tensor().
     # =========================================================================

+    @app.post("/data/batch")
+    async def retrieve_data_shard_batch(request: Request):
+        """Retrieve multiple tensor shards in one request.
+
+        Mirrors the ``POST /data/batch`` endpoint on the Flask RPC server
+        (``rpc_server.py``) so that ``HttpRTensorBackend._fetch_shard_group``
+        works against data-proxy addresses.
+        """
+        try:
+            try:
+                payload = (await request.json()) or {}
+            except Exception:
+                payload = {}
+            if not isinstance(payload, dict):
+                payload = {}
+            shard_ids = payload.get("shard_ids", [])
+            if not isinstance(shard_ids, list) or not all(
+                isinstance(sid, str) for sid in shard_ids
+            ):
+                return JSONResponse(
+                    status_code=400,
+                    content={
+                        "status": "error",
+                        "message": "Expected JSON body with string list field 'shard_ids'",
+                    },
+                )
+
+            data = []
+            missing: list[str] = []
+            for sid in shard_ids:
+                try:
+                    data.append(rtensor_storage.fetch(sid))
+                except KeyError:
+                    missing.append(sid)
+
+            if missing:
+                return JSONResponse(
+                    status_code=400,
+                    content={
+                        "status": "error",
+                        "message": "One or more requested shards were not found",
+                        "missing_shard_ids": missing,
+                    },
+                )
+
+            serialized_data = serialize_value(data)
+            data_bytes = orjson.dumps(serialized_data)
+            logger.debug(
+                "Retrieved %d RTensor shards in batch (size=%d bytes)",
+                len(shard_ids),
+                len(data_bytes),
+            )
+            return RawResponse(
+                content=data_bytes, media_type="application/octet-stream"
+            )
+        except Exception as e:
+            logger.error("Error retrieving batch shards: %s", e, exc_info=True)
+            return JSONResponse(
+                status_code=500,
+                content={"status": "error", "message": str(e)},
+            )
+
     @app.put("/data/{shard_id}")
     async def store_data_shard(shard_id: str, request: Request):
         """Store a tensor shard in local RTensor storage."""

PATCH

echo "Patch applied successfully."
