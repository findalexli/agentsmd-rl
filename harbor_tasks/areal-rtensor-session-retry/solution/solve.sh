#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if _create_session already exists, patch was applied
if grep -q '_create_session' areal/infra/rpc/rtensor.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/infra/rpc/rtensor.py b/areal/infra/rpc/rtensor.py
index 510411d9f..2fc90593f 100644
--- a/areal/infra/rpc/rtensor.py
+++ b/areal/infra/rpc/rtensor.py
@@ -13,6 +13,10 @@
 import torch

 from areal.infra.utils.concurrent import run_async_task
+from areal.infra.utils.http import DEFAULT_REQUEST_TIMEOUT, get_default_connector
+from areal.utils import logging
+
+logger = logging.getLogger("HttpRTensor")


 class RTensorBackend(Protocol):
@@ -79,19 +83,60 @@ class TensorShardInfo:


 class HttpRTensorBackend:
+    def _create_session(self) -> aiohttp.ClientSession:
+        """Create a properly configured aiohttp session for large tensor transfers."""
+        timeout = aiohttp.ClientTimeout(
+            total=DEFAULT_REQUEST_TIMEOUT,
+            sock_connect=DEFAULT_REQUEST_TIMEOUT,
+            connect=DEFAULT_REQUEST_TIMEOUT,
+        )
+        return aiohttp.ClientSession(
+            timeout=timeout,
+            read_bufsize=10 * 1024 * 1024,  # 10MB buffer
+            connector=get_default_connector(),
+        )
+
     async def _fetch_tensor(
-        self, session: aiohttp.ClientSession, shard_id: str, node_addr: str
+        self,
+        session: aiohttp.ClientSession,
+        shard_id: str,
+        node_addr: str,
+        max_retries: int = 3,
+        retry_delay: float = 1.0,
     ) -> torch.Tensor:
         # Avoid circular import
         from areal.infra.rpc.serialization import deserialize_value

         url = f"http://{node_addr}/data/{shard_id}"
-        async with session.get(url) as resp:
-            if resp.status != 200:
-                raise RuntimeError(f"Failed to fetch shard from {url}: {resp.status}")
-            data_bytes = await resp.read()
-            serialized_data = orjson.loads(data_bytes)
-            return deserialize_value(serialized_data)
+        last_exception = None
+
+        for attempt in range(max_retries):
+            try:
+                async with session.get(url) as resp:
+                    if resp.status != 200:
+                        raise RuntimeError(
+                            f"Failed to fetch shard from {url}: {resp.status}"
+                        )
+                    data_bytes = await resp.read()
+                    serialized_data = orjson.loads(data_bytes)
+                    return deserialize_value(serialized_data)
+            except (TimeoutError, aiohttp.ClientError) as e:
+                last_exception = e
+                logger.warning(
+                    "RTensor fetch from %s failed: %s: %s (attempt %d/%d)",
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
+            f"Failed to fetch shard from {url} after {max_retries} attempts. "
+            f"Last error: {repr(last_exception)}"
+        )

     def fetch(self, shards: list[TensorShardInfo]) -> list[torch.Tensor]:
         """Fetch multiple shards concurrently via HTTP using a single session."""
@@ -99,7 +144,7 @@ def fetch(self, shards: list[TensorShardInfo]) -> list[torch.Tensor]:
             return []

         async def _fetch():
-            async with aiohttp.ClientSession() as session:
+            async with self._create_session() as session:
                 tasks = [
                     self._fetch_tensor(session, s.shard_id, s.node_addr) for s in shards
                 ]
@@ -115,7 +160,7 @@ def store(self, tensor: torch.Tensor) -> str:

     async def delete(self, node_addr: str, shard_ids: list[str]) -> None:
         """Delete shards via HTTP DELETE request."""
-        async with aiohttp.ClientSession() as session:
+        async with self._create_session() as session:
             async with session.delete(
                 f"http://{node_addr}/data/clear", json={"shard_ids": shard_ids}
             ) as resp:
diff --git a/areal/utils/logging.py b/areal/utils/logging.py
index 5d29cbe88..52a9cbf21 100644
--- a/areal/utils/logging.py
+++ b/areal/utils/logging.py
@@ -59,6 +59,7 @@
     "SyncRPCServer": "white",
     "RayRPCServer": "white",
     "RPCSerialization": "white",
+    "HttpRTensor": "white",
     # Inference wrappers - white
     "SGLangWrapper": "white",
     "VLLMWrapper": "white",

PATCH

echo "Patch applied successfully."
