#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied (check for retry_interval in aclose signature)
grep -q 'async def aclose(self, timeout=' gradio/utils.py && exit 0

git apply - <<'PATCH'
diff --git a/gradio/utils.py b/gradio/utils.py
index 2cf7f35585..327dbf8b4d 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -867,8 +867,17 @@ async def __anext__(self):
             run_sync_iterator_async, self.iterator, limiter=self.limiter
         )

-    async def aclose(self):
-        self.iterator.close()
+    async def aclose(self, timeout=60.0, retry_interval=0.05):
+        start = time.monotonic()
+        while True:
+            try:
+                self.iterator.close()
+                break
+            except ValueError as e:
+                if "already executing" in str(e) and time.monotonic() - start < timeout:
+                    await asyncio.sleep(retry_interval)
+                else:
+                    raise


 async def async_iteration(iterator):
@@ -1928,28 +1937,13 @@ def get_function_description(fn: Callable) -> tuple[str, dict[str, str], list[st
     return description, parameters, returns


-async def safe_aclose_iterator(iterator, timeout=60.0, retry_interval=0.05):
+async def safe_aclose_iterator(iterator):
     """
-    Safely close generators by calling the aclose method.
-    Sync generators are tricky because if you call `aclose` while the loop is running
-    then you get a ValueError and the generator will not shut down gracefully.
-    So the solution is to retry calling the aclose method until we succeed (with timeout).
+    Safely close an async iterator by calling its aclose method.
+    For SyncToAsyncIterator, the retry logic for "generator already executing"
+    is handled in SyncToAsyncIterator.aclose() itself.
     """
-    start = time.monotonic()
-    if isinstance(iterator, SyncToAsyncIterator):
-        while True:
-            try:
-                await iterator.aclose()
-                break
-            except ValueError as e:
-                if "already executing" in str(e):
-                    if time.monotonic() - start > timeout:
-                        raise
-                    await asyncio.sleep(retry_interval)
-                else:
-                    raise
-    else:
-        await iterator.aclose()
+    await iterator.aclose()


 def set_default_buttons(
PATCH
