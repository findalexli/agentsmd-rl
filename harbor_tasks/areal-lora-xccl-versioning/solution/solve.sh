#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

# Idempotent: skip if already applied
grep -q 'request: UpdateWeightsFromXcclRequestLora' areal/engine/vllm_ext/areal_vllm_server.py && exit 0

git apply - <<'PATCH'
diff --git a/areal/engine/vllm_ext/areal_vllm_server.py b/areal/engine/vllm_ext/areal_vllm_server.py
index d3b269bd6..ba0228126 100644
--- a/areal/engine/vllm_ext/areal_vllm_server.py
+++ b/areal/engine/vllm_ext/areal_vllm_server.py
@@ -152,12 +152,33 @@ async def update_weight_xccl(raw_request: Request):


 @router.post("/areal_update_weights_lora_xccl")
-async def update_weight_lora_xccl(raw_request: Request):
+async def update_weight_lora_xccl(
+    request: UpdateWeightsFromXcclRequestLora, raw_request: Request
+):
     logger.info("API server starts update_weight_lora via XCCL")
     llm = raw_request.app.state.engine_client
     ret_list = await llm.engine_core.call_utility_async(
         "areal_injected_update_weight_lora_xccl",
     )
+    # Only touch the registry after weights are actually updated
+    models_obj = raw_request.app.state.openai_serving_models
+    new_name = request.lora_name
+    lora_id = request.lora_int_id
+    for old_name, req in list(models_obj.lora_requests.items()):
+        if req.lora_int_id == lora_id:
+            del models_obj.lora_requests[old_name]
+            req.lora_name = new_name
+            models_obj.lora_requests[new_name] = req
+            logger.info(
+                f"Updated LoRA name of openai_serving_models "
+                f"from {old_name} -> {new_name}"
+            )
+            break
+    else:
+        logger.warning(
+            f"LoRA adapter with int_id={lora_id} not found in "
+            f"openai_serving_models.lora_requests"
+        )
     return build_response(ret_list)


diff --git a/areal/engine/vllm_remote.py b/areal/engine/vllm_remote.py
index 84443e391..3a6f236e1 100644
--- a/areal/engine/vllm_remote.py
+++ b/areal/engine/vllm_remote.py
@@ -185,7 +185,7 @@ def build_distributed_weight_update_requests(
                 ),
                 HttpRequest(
                     endpoint=update_endpoint,
-                    payload={},
+                    payload={} if not meta.use_lora else payload,
                 ),
             ]
         )
PATCH
