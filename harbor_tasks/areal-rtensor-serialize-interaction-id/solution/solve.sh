#!/usr/bin/env bash
set -euo pipefail

cd /repos/AReaL

# Idempotency check: if the setter already exists, patch is applied
if grep -q '_interaction_id' areal/experimental/openai/types.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/experimental/inference_service/data_proxy/app.py b/areal/experimental/inference_service/data_proxy/app.py
index f1a43293b..04832d5ed 100644
--- a/areal/experimental/inference_service/data_proxy/app.py
+++ b/areal/experimental/inference_service/data_proxy/app.py
@@ -359,14 +359,16 @@ async def export_trajectories(
         store.remove_session(body.session_id)

         # Serialize for HTTP transport, storing tensors locally as RTensor shards
-        # so that RTensor.localize() on the client can fetch them via /data/ endpoints.
-        serving_addr = config.serving_addr
-        if not serving_addr:
-            logger.warning(
-                "serving_addr not configured; tensors will be serialized "
-                "as plain lists (RTensor.localize() will not work remotely)"
-            )
-        serialized = serialize_interactions(interactions, node_addr=serving_addr)
+        from areal.infra.rpc.rtensor import RTensor
+
+        for item in interactions.values():
+            # Set the internal cache
+            item.to_tensor_dict()
+            # Remotize the tensor dict cache
+            item._cache = RTensor.remotize(item._cache, node_addr=config.serving_addr)
+
+        # serialize RTensors
+        serialized = serialize_interactions(interactions)
         return ExportTrajectoriesResponse(interactions=serialized)

     # NOTE: /grant_capacity has been removed from data proxy. Capacity-based
diff --git a/areal/experimental/openai/proxy/server.py b/areal/experimental/openai/proxy/server.py
index 70639d174..f499d0623 100644
--- a/areal/experimental/openai/proxy/server.py
+++ b/areal/experimental/openai/proxy/server.py
@@ -5,7 +5,6 @@
 import time
 from typing import TYPE_CHECKING, Any

-import torch
 from pydantic import BaseModel

 from areal.experimental.openai.cache import InteractionCache
@@ -127,114 +126,35 @@ def export_interactions(

 def serialize_interactions(
     interactions: dict[str, InteractionWithTokenLogpReward],
-    node_addr: str = "",
 ) -> dict[str, Any]:
-    """Serialize interactions for HTTP transport.
-
-    When ``node_addr`` is provided, tensors are stored in the local RTensor
-    storage (on the data proxy process) and only shard metadata is serialized.
-    This enables ``RTensor.localize()`` on the client to fetch tensors via
-    HTTP GET ``/data/{shard_id}`` from the data proxy.
-
-    When ``node_addr`` is empty (legacy mode), tensors are serialized as
-    plain lists for backward compatibility.
-
-    Parameters
-    ----------
-    interactions : dict[str, InteractionWithTokenLogpReward]
-        Interactions to serialize
-    node_addr : str
-        Data proxy's serving address (host:port) for RTensor shard storage.
-        If empty, falls back to plain tensor serialization.
-    """
-    from areal.infra.rpc.rtensor import get_backend
+    """Serialize interactions into a json-compatible format for HTTP transport."""
+    from areal.infra.rpc.serialization import serialize_value

     result = {}
     for key, interaction in interactions.items():
-        tensor_dict = interaction.to_tensor_dict()
-
-        if node_addr:
-            # Store tensors locally on the data proxy and serialize shard metadata
-            shard_dict = {}
-            shapes = {}
-            dtypes = {}
-            for k, v in tensor_dict.items():
-                tensor = v.detach().cpu()
-                shard_id = get_backend().store(tensor)
-                shard_dict[k] = {
-                    "shard_id": shard_id,
-                    "node_addr": node_addr,
-                }
-                shapes[k] = list(tensor.shape)
-                dtypes[k] = str(tensor.dtype)
-            result[key] = {
-                "shard_dict": shard_dict,
-                "shapes": shapes,
-                "dtypes": dtypes,
-                "reward": interaction.reward,
-                "interaction_id": interaction.interaction_id,
-            }
-        else:
-            # Legacy mode: serialize tensors as plain lists
-            result[key] = {
-                "tensor_dict": {k: v.tolist() for k, v in tensor_dict.items()},
-                "reward": interaction.reward,
-                "interaction_id": interaction.interaction_id,
-            }
-    return result
+        result[key] = {
+            "tensor_dict": interaction.to_tensor_dict(),
+            "reward": interaction.reward,
+            "interaction_id": interaction.interaction_id,
+        }
+    return serialize_value(result)


 def deserialize_interactions(
     data: dict[str, Any],
 ) -> dict[str, InteractionWithTokenLogpReward]:
-    """Deserialize interactions from HTTP response.
-
-    Supports two formats:
-
-    1. **Shard metadata format** (``shard_dict`` key present): RTensors are
-       reconstructed from shard metadata. The actual tensor data stays on the
-       data proxy and will be fetched lazily via ``RTensor.localize()``.
-
-    2. **Legacy format** (``tensor_dict`` key present): Tensors are
-       reconstructed from plain lists and re-remotized locally. This path
-       exists for backward compatibility with data proxies that don't
-       support RTensor storage.
-    """
-    from areal.experimental.openai.types import (
-        InteractionWithTokenLogpReward,
-    )
-    from areal.infra.rpc.rtensor import RTensor, TensorShardInfo
+    """Deserialize interactions from HTTP response."""
+    from areal.experimental.openai.types import InteractionWithTokenLogpReward
+    from areal.infra.rpc.serialization import deserialize_value

+    data = deserialize_value(data)
     result = {}
     for key, item in data.items():
-        if "shard_dict" in item:
-            # Shard metadata format: reconstruct RTensors from shard info
-            tensor_dict = {}
-            for k, shard_info in item["shard_dict"].items():
-                shape = item["shapes"][k]
-                dtype_str = item["dtypes"][k].replace("torch.", "")
-                dtype = getattr(torch, dtype_str)
-                shard = TensorShardInfo(
-                    shard_id=shard_info["shard_id"],
-                    node_addr=shard_info["node_addr"],
-                )
-                # Create RTensor with meta placeholder — data fetched on localize()
-                tensor_dict[k] = RTensor(
-                    shard=shard,
-                    data=torch.empty(shape, dtype=dtype, device="meta"),
-                )
-        else:
-            # Legacy format: reconstruct tensors and remotize locally
-            from areal.utils.network import gethostip
-
-            node_addr = gethostip()
-            tensor_dict = {k: torch.tensor(v) for k, v in item["tensor_dict"].items()}
-            tensor_dict = RTensor.remotize(tensor_dict, node_addr=node_addr)
-
         # Create a minimal InteractionWithTokenLogpReward with cached tensor dict
         interaction = InteractionWithTokenLogpReward()
-        interaction._cache = tensor_dict
+        interaction._cache = item["tensor_dict"]
         interaction.reward = item["reward"]
+        interaction.interaction_id = item["interaction_id"]
         result[key] = interaction
     return result

diff --git a/areal/experimental/openai/types.py b/areal/experimental/openai/types.py
index 21bb95481..28a0c727b 100644
--- a/areal/experimental/openai/types.py
+++ b/areal/experimental/openai/types.py
@@ -52,6 +52,9 @@ class InteractionWithTokenLogpReward:
     response: Response | None = None
     input_data: str | ResponseInputParam = field(default_factory=lambda: "")

+    # Interaction ID cache (used for deserialization)
+    _interaction_id: str | None = None
+
     @property
     def is_completion(self) -> bool:
         return self.completion is not None
@@ -101,9 +104,17 @@ def interaction_id(self) -> str | None:
             return self.completion.id
         elif self.is_response:
             return self.response.id
+        elif self._interaction_id is not None:
+            return self._interaction_id
         else:
             return None

+    @interaction_id.setter
+    def interaction_id(self, value):
+        if self.is_completion or self.is_response:
+            raise ValueError("Cannot set ID for completion or responses")
+        self._interaction_id = value
+
     @property
     def created_at(self) -> float | None:
         if self.is_completion:

PATCH

echo "Patch applied successfully."
