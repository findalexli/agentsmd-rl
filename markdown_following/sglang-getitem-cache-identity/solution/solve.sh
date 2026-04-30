#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q '_sub_obj_cache' python/sglang/srt/managers/io_struct.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/io_struct.py b/python/sglang/srt/managers/io_struct.py
index bd979653458a..82d6fa0642c3 100644
--- a/python/sglang/srt/managers/io_struct.py
+++ b/python/sglang/srt/managers/io_struct.py
@@ -601,7 +601,12 @@ def _validate_session_params(self):
                 raise ValueError("Session params must be a dict or a list of dicts.")

     def __getitem__(self, i):
-        return GenerateReqInput(
+        # Cache sub-objects so that repeated obj[i] calls return the same instance.
+        # This avoids subtle bugs where different call sites get divergent objects.
+        cache = self.__dict__.setdefault("_sub_obj_cache", {})
+        if i in cache:
+            return cache[i]
+        sub = GenerateReqInput(
             text=self.text[i] if self.text is not None else None,
             input_ids=self.input_ids[i] if self.input_ids is not None else None,
             input_embeds=(
@@ -665,6 +670,8 @@ def __getitem__(self, i):
             http_worker_ipc=self.http_worker_ipc,
             received_time=self.received_time,
         )
+        cache[i] = sub
+        return sub


 @dataclass
@@ -890,8 +897,13 @@ def contains_mm_input(self) -> bool:
         )

     def __getitem__(self, i):
+        # Cache sub-objects so that repeated obj[i] calls return the same instance.
+        cache = self.__dict__.setdefault("_sub_obj_cache", {})
+        if i in cache:
+            return cache[i]
+
         if self.is_cross_encoder_request:
-            return EmbeddingReqInput(
+            sub = EmbeddingReqInput(
                 text=[self.text[i]] if self.text is not None else None,
                 sampling_params=self.sampling_params[i],
                 rid=self.rid[i],
@@ -900,22 +912,24 @@ def __getitem__(self, i):
                 is_cross_encoder_request=True,
                 http_worker_ipc=self.http_worker_ipc,
             )
-
-        return EmbeddingReqInput(
-            text=self.text[i] if self.text is not None else None,
-            input_ids=self.input_ids[i] if self.input_ids is not None else None,
-            image_data=self.image_data[i] if self.image_data is not None else None,
-            audio_data=self.audio_data[i] if self.audio_data is not None else None,
-            video_data=self.video_data[i] if self.video_data is not None else None,
-            sampling_params=self.sampling_params[i],
-            rid=self.rid[i],
-            lora_path=self.lora_path[i] if self.lora_path is not None else None,
-            lora_id=self.lora_id[i] if self.lora_id is not None else None,
-            external_trace_header=self.external_trace_header,
-            dimensions=self.dimensions,
-            http_worker_ipc=self.http_worker_ipc,
-            received_time=self.received_time,
-        )
+        else:
+            sub = EmbeddingReqInput(
+                text=self.text[i] if self.text is not None else None,
+                input_ids=self.input_ids[i] if self.input_ids is not None else None,
+                image_data=self.image_data[i] if self.image_data is not None else None,
+                audio_data=self.audio_data[i] if self.audio_data is not None else None,
+                video_data=self.video_data[i] if self.video_data is not None else None,
+                sampling_params=self.sampling_params[i],
+                rid=self.rid[i],
+                lora_path=self.lora_path[i] if self.lora_path is not None else None,
+                lora_id=self.lora_id[i] if self.lora_id is not None else None,
+                external_trace_header=self.external_trace_header,
+                dimensions=self.dimensions,
+                http_worker_ipc=self.http_worker_ipc,
+                received_time=self.received_time,
+            )
+        cache[i] = sub
+        return sub


 @dataclass
diff --git a/python/sglang/srt/managers/tokenizer_manager.py b/python/sglang/srt/managers/tokenizer_manager.py
index 71e8cf5d2471..2f2876a8d39f 100644
--- a/python/sglang/srt/managers/tokenizer_manager.py
+++ b/python/sglang/srt/managers/tokenizer_manager.py
@@ -2335,6 +2335,11 @@ async def _resolve_lora_path(self, obj: Union[GenerateReqInput, EmbeddingReqInpu

         # Look up the LoRA ID from the registry and start tracking ongoing LoRA requests.
         obj.lora_id = await self.lora_registry.acquire(obj.lora_path)
+        # Propagate lora_id to any sub-objects already cached by __getitem__.
+        for i, sub_obj in obj.__dict__.get("_sub_obj_cache", {}).items():
+            sub_obj.lora_id = (
+                obj.lora_id[i] if isinstance(obj.lora_id, list) else obj.lora_id
+            )

     def _req_stats_init(
         self,
PATCH

echo "Patch applied successfully."
