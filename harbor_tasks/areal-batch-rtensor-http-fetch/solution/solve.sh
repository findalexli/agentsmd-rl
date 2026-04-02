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

git apply - <<'PATCH'
diff --git a/areal/infra/rpc/rtensor.py b/areal/infra/rpc/rtensor.py
index 2fc90593f..fc06eda1b 100644
--- a/areal/infra/rpc/rtensor.py
+++ b/areal/infra/rpc/rtensor.py
@@ -5,7 +5,7 @@
 from collections import defaultdict
 from dataclasses import dataclass
 from threading import Lock
-from typing import Any, Protocol
+from typing import Any, Protocol, cast

 import aiohttp
 import orjson
@@ -83,6 +83,11 @@ class TensorShardInfo:


 class HttpRTensorBackend:
+    def __init__(self, max_shards_per_request: int = 32) -> None:
+        if max_shards_per_request <= 0:
+            raise ValueError("max_shards_per_request must be positive")
+        self.max_shards_per_request = max_shards_per_request
+
     def _create_session(self) -> aiohttp.ClientSession:
         """Create a properly configured aiohttp session for large tensor transfers."""
         timeout = aiohttp.ClientTimeout(
@@ -114,8 +119,10 @@ async def _fetch_tensor(
             try:
                 async with session.get(url) as resp:
                     if resp.status != 200:
+                        error_body = (await resp.text()).strip()
+                        detail = f" body={error_body}" if error_body else ""
                         raise RuntimeError(
-                            f"Failed to fetch shard from {url}: {resp.status}"
+                            f"Failed to fetch shard from {url}: {resp.status}{detail}"
                         )
                     data_bytes = await resp.read()
                     serialized_data = orjson.loads(data_bytes)
@@ -138,17 +145,96 @@ async def _fetch_tensor(
             f"Last error: {repr(last_exception)}"
         )

+    async def _fetch_shard_group(
+        self,
+        session: aiohttp.ClientSession,
+        node_addr: str,
+        grouped: list[tuple[int, TensorShardInfo]],
+        max_retries: int = 3,
+        retry_delay: float = 1.0,
+    ) -> list[torch.Tensor]:
+        from areal.infra.rpc.serialization import deserialize_value
+
+        shard_ids = [shard.shard_id for _, shard in grouped]
+        url = f"http://{node_addr}/data/batch"
+        last_exception = None
+
+        for attempt in range(max_retries):
+            try:
+                async with session.post(url, json={"shard_ids": shard_ids}) as resp:
+                    if resp.status != 200:
+                        error_body = (await resp.text()).strip()
+                        detail = f" body={error_body}" if error_body else ""
+                        raise RuntimeError(
+                            f"Failed to fetch shard batch from {url}: {resp.status}{detail}"
+                        )
+
+                    data_bytes = await resp.read()
+                    serialized_data = orjson.loads(data_bytes)
+                    tensors = cast(
+                        list[torch.Tensor], deserialize_value(serialized_data)
+                    )
+                    if len(tensors) != len(grouped):
+                        raise RuntimeError(
+                            f"Batch fetch from {url} returned {len(tensors)} shards for {len(grouped)} requested"
+                        )
+                    return tensors
+            except (TimeoutError, aiohttp.ClientError) as e:
+                last_exception = e
+                logger.warning(
+                    "RTensor batch fetch from %s failed: %s: %s (attempt %d/%d)",
+                    url,
+                    e.__class__.__name__,
+                    str(e),
+                    attempt + 1,
+                    max_retries,
+                )
+                if attempt < max_retries - 1:
+                    await asyncio.sleep(retry_delay)
+
+        raise RuntimeError(
+            f"Failed to fetch shard batch from {url} after {max_retries} attempts. "
+            f"Last error: {repr(last_exception)}"
+        )
+
     def fetch(self, shards: list[TensorShardInfo]) -> list[torch.Tensor]:
         """Fetch multiple shards concurrently via HTTP using a single session."""
         if not shards:
             return []

         async def _fetch():
+            indexed_shards = list(enumerate(shards))
+            shards_by_node: dict[str, list[tuple[int, TensorShardInfo]]] = defaultdict(
+                list
+            )
+            for index, shard in indexed_shards:
+                shards_by_node[shard.node_addr].append((index, shard))
+
+            results: list[torch.Tensor | None] = [None] * len(shards)
+
             async with self._create_session() as session:
-                tasks = [
-                    self._fetch_tensor(session, s.shard_id, s.node_addr) for s in shards
-                ]
-                return await asyncio.gather(*tasks)
+
+                async def _fetch_node(
+                    node_addr: str, grouped: list[tuple[int, TensorShardInfo]]
+                ) -> None:
+                    for start in range(0, len(grouped), self.max_shards_per_request):
+                        chunk = grouped[start : start + self.max_shards_per_request]
+                        tensors = await self._fetch_shard_group(
+                            session, node_addr, chunk
+                        )
+                        for (original_index, _), tensor in zip(
+                            chunk, tensors, strict=True
+                        ):
+                            results[original_index] = tensor
+
+                await asyncio.gather(
+                    *[
+                        _fetch_node(node_addr, grouped)
+                        for node_addr, grouped in shards_by_node.items()
+                    ]
+                )
+
+            return cast(list[torch.Tensor], results)

         return run_async_task(_fetch)

PATCH
