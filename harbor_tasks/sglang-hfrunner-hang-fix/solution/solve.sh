#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

# Idempotent: skip if already applied
grep -q 'import queue as queue_mod' python/sglang/test/runners.py && exit 0

git apply - <<'PATCH'
diff --git a/python/sglang/test/runners.py b/python/sglang/test/runners.py
index 61781fea21de..8edd4fa802f7 100644
--- a/python/sglang/test/runners.py
+++ b/python/sglang/test/runners.py
@@ -15,6 +15,7 @@
 import json
 import multiprocessing as mp
 import os
+import queue as queue_mod
 from dataclasses import dataclass
 from typing import Any, List, Optional, Tuple, Union

@@ -411,7 +412,16 @@ def forward(
         self.in_queue.put(
             (prompts, image_data, max_new_tokens, lora_paths, token_ids_logprob)
         )
-        return self.out_queue.get()
+        while True:
+            try:
+                return self.out_queue.get(timeout=5)
+            except queue_mod.Empty:
+                if not self.model_proc.is_alive() and self.out_queue.empty():
+                    exitcode = self.model_proc.exitcode
+                    raise RuntimeError(
+                        f"HFRunner subprocess died with exit code {exitcode} "
+                        f"before producing output"
+                    )

     def terminate(self):
         self.model_proc.terminate()
PATCH
