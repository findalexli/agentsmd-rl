#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency: check if the enum classes already exist
if grep -q "class ApiType" areal/experimental/openai/types.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/experimental/openai/types.py b/areal/experimental/openai/types.py
index 1f9837d6a..21bb95481 100644
--- a/areal/experimental/openai/types.py
+++ b/areal/experimental/openai/types.py
@@ -1,6 +1,7 @@
 from __future__ import annotations  # noqa

 from dataclasses import dataclass, field
+from enum import Enum

 import torch
 from openai.types.chat import ChatCompletion
@@ -13,6 +14,22 @@
 logger = logging.getLogger("TokenLogpReward")


+class ApiType(str, Enum):
+    """API type for interaction."""
+
+    COMPLETION = "completion"
+    RESPONSE = "response"
+    NONE = "none"
+
+
+class InputName(str, Enum):
+    """Input name used for logging."""
+
+    MESSAGES = "messages"
+    INPUT_DATA = "input_data"
+    NONE = "none"
+
+
 @dataclass
 class InteractionWithTokenLogpReward:
     """Internal structure to store completions/responses with their rewards."""
@@ -44,25 +61,24 @@ def is_response(self) -> bool:
         return self.response is not None

     @property
-    def api_type(self) -> str:
-        # TODO: replace api_type value with enum
+    def api_type(self) -> ApiType:
         """API type (completion/response)."""
         if self.is_completion:
-            return "completion"
+            return ApiType.COMPLETION
         elif self.is_response:
-            return "response"
+            return ApiType.RESPONSE
         else:
-            return "none"
+            return ApiType.NONE

     @property
-    def input_name_for_logging(self) -> str:
-        # TODO: replace input_name value with enum
+    def input_name_for_logging(self) -> InputName:
+        """Input name used for logging."""
         if self.is_completion:
-            return "messages"
+            return InputName.MESSAGES
         elif self.is_response:
-            return "input_data"
+            return InputName.INPUT_DATA
         else:
-            return "none"
+            return InputName.NONE

     @property
     def current_data(self) -> list[dict] | str | ResponseInputParam | None:
@@ -143,7 +159,7 @@ def to_tensor_dict(self) -> dict[str, torch.Tensor]:
                 logger.warning(
                     f"The input length of the child {api_type} ({resp.input_len}) is less than or "
                     f"equal to the length of the parent {api_type} {parent_len}. "
-                    f"This should not happen if the {input_name}s are constructed properly."
+                    f"This should not happen if the {input_name}s are constructed properly. "
                     f"Ignoring the parent {api_type} by masking them out. \n"
                     f"Parent input token ids: {self.parent.model_response.input_tokens}\n"
                     f"Parent output token ids: {self.parent.model_response.output_tokens}\n"
diff --git a/areal/reward/clevr_count_70k.py b/areal/reward/clevr_count_70k.py
index 553b999f9..c3c0b039f 100644
--- a/areal/reward/clevr_count_70k.py
+++ b/areal/reward/clevr_count_70k.py
@@ -1,5 +1,9 @@
 import re

+from areal.utils import logging
+
+logger = logging.getLogger("CLEVR70KReward")
+

 def extract_answer(pred_str, data_name, use_last_number=True):
     match = re.findall(r"\[([0-9\.]+)\]", pred_str)
@@ -11,17 +15,16 @@ def extract_answer(pred_str, data_name, use_last_number=True):

 def clevr_count_70k_reward_fn(
     prompt, completions, prompt_ids, completion_ids, answer, **kwargs
-):
+) -> float:
     sol = extract_answer(completions, data_name="")  # str number
     ans = answer

     if sol is None:
-        return 0
+        return 0.0
     if ans is None:
-        return 0
-
-    if sol.strip() == ans.strip():
-        print(f"completions: {completions}, answer: {answer}")
-        return 1
+        return 0.0

-    return 0
+    is_correct = sol.strip() == ans.strip()
+    if is_correct:
+        logger.info(f"completions: {completions}, answer: {answer}")
+    return float(is_correct)

PATCH

echo "Patch applied successfully."
