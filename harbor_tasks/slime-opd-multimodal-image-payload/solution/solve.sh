#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency: check if fix is already applied
if grep -q 'encode_image_for_rollout_engine' slime/rollout/on_policy_distillation.py; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/rollout/on_policy_distillation.py b/slime/rollout/on_policy_distillation.py
index cf25b4897..919097434 100644
--- a/slime/rollout/on_policy_distillation.py
+++ b/slime/rollout/on_policy_distillation.py
@@ -1,6 +1,7 @@
 import aiohttp
 import torch

+from slime.utils.processing_utils import encode_image_for_rollout_engine
 from slime.utils.types import Sample


@@ -16,6 +17,11 @@ async def reward_func(args, sample, **kwargs):
         "return_logprob": True,
         "logprob_start_len": 0,
     }
+
+    if sample.multimodal_inputs and sample.multimodal_inputs.get("images"):
+        image_data = sample.multimodal_inputs["images"]
+        payload["image_data"] = [encode_image_for_rollout_engine(image) for image in image_data]
+
     session_kwargs = {}
     async with aiohttp.ClientSession(**session_kwargs) as session:
         async with session.post(args.rm_url, json=payload) as resp:

PATCH

echo "Fix applied successfully."
