#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'flash_attn.cute.cache_utils' python/sglang/multimodal_gen/runtime/utils/logging_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py b/python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py
index a8aeddf972d3..d4473b0e1ada 100644
--- a/python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py
+++ b/python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py
@@ -259,7 +259,7 @@ def forward(
         mask_function = create_causal_mask
         causal_mask = mask_function(
             config=self.config,
-            input_embeds=inputs_embeds,
+            inputs_embeds=inputs_embeds,
             attention_mask=attention_mask,
             cache_position=cache_position,
             past_key_values=past_key_values,
diff --git a/python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py b/python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py
index 160838522fb4..bdd5d2a16eab 100644
--- a/python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py
+++ b/python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py
@@ -434,7 +434,7 @@ def forward(
             # Prepare mask arguments
             mask_kwargs = {
                 "config": self.config,
-                "input_embeds": inputs_embeds,
+                "inputs_embeds": inputs_embeds,
                 "attention_mask": attention_mask,
                 "cache_position": cache_position,
                 "past_key_values=past_key_values,
diff --git a/python/sglang/multimodal_gen/runtime/utils/logging_utils.py b/python/sglang/multimodal_gen/runtime/utils/logging_utils.py
index 1b13c05c6d70..6c55c8d187fb 100644
--- a/python/sglang/multimodal_gen/runtime/utils/logging_utils.py
+++ b/python/sglang/multimodal_gen/runtime/utils/logging_utils.py
@@ -562,6 +562,7 @@ def globally_suppress_loggers():
         "urllib3",
         "httpx",
         "httpcore",
+        "flash_attn.cute.cache_utils",
     ]

     for name in target_names:
diff --git a/python/sglang/srt/utils/json_response.py b/python/sglang/srt/utils/json_response.py
index 03130c61a4e8..aa13dfb2cfa9 100644
--- a/python/sglang/srt/utils/json_response.py
+++ b/python/sglang/srt/utils/json_response.py
@@ -3,7 +3,7 @@
 from typing import Any

 import orjson
-from fastapi.responses import ORJSONResponse, Response
+from fastapi.responses import Response

 # Keep response serialization behavior consistent across endpoints:
 # - Support non-string dictionary keys used in some metadata payloads.
@@ -16,17 +16,15 @@ def dumps_json(content: Any) -> bytes:
     return orjson.dumps(content, option=ORJSON_RESPONSE_OPTIONS)


-class SGLangORJSONResponse(ORJSONResponse):
+class SGLangORJSONResponse(Response):
     """ORJSON response with SGLang-specific serialization options."""

+    media_type = "application/json"
+
     def render(self, content: Any) -> bytes:
         return dumps_json(content)


 def orjson_response(content: Any, status_code: int = 200) -> Response:
     """Create a JSON response with stable ORJSON serialization options."""
-    return Response(
-        content=dumps_json(content),
-        media_type="application/json",
-        status_code=status_code,
-    )
+    return SGLangORJSONResponse(content=content, status_code=status_code)

PATCH

echo "Patch applied successfully."
