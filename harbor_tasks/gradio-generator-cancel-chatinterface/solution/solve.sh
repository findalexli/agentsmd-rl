#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied
grep -q 'aclosing' gradio/chat_interface.py && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/gradio/chat_interface.py b/gradio/chat_interface.py
index 208f5001ab..b52a4e8e32 100644
--- a/gradio/chat_interface.py
+++ b/gradio/chat_interface.py
@@ -11,6 +11,7 @@
 import os
 import warnings
 from collections.abc import AsyncGenerator, Callable, Generator
+from contextlib import aclosing
 from functools import wraps
 from typing import Any, Literal, Union, cast

@@ -959,27 +960,30 @@ async def _stream_fn(

         history = self._append_message_to_history(message, history, "user")
         additional_outputs = None
-        try:
-            first_response = await utils.async_iteration(generator)
-            if self.additional_outputs:
-                first_response, *additional_outputs = first_response
-            history_ = self._append_message_to_history(
-                first_response, history, "assistant"
-            )
-            if not additional_outputs:
-                yield first_response, history_
-            else:
-                yield first_response, history_, *additional_outputs
-        except StopIteration:
-            yield None, history
-        async for response in generator:
-            if self.additional_outputs:
-                response, *additional_outputs = response
-            history_ = self._append_message_to_history(response, history, "assistant")
-            if not additional_outputs:
-                yield response, history_
-            else:
-                yield response, history_, *additional_outputs
+        async with aclosing(generator):
+            try:
+                first_response = await utils.async_iteration(generator)
+                if self.additional_outputs:
+                    first_response, *additional_outputs = first_response
+                history_ = self._append_message_to_history(
+                    first_response, history, "assistant"
+                )
+                if not additional_outputs:
+                    yield first_response, history_
+                else:
+                    yield first_response, history_, *additional_outputs
+            except StopIteration:
+                yield None, history
+            async for response in generator:
+                if self.additional_outputs:
+                    response, *additional_outputs = response
+                history_ = self._append_message_to_history(
+                    response, history, "assistant"
+                )
+                if not additional_outputs:
+                    yield response, history_
+                else:
+                    yield response, history_, *additional_outputs

     def option_clicked(
         self, history: list[MessageDict], option: SelectData
@@ -1082,8 +1086,9 @@ async def _examples_stream_fn(
         else:
             generator = await run_sync(self.fn, *inputs, limiter=self.limiter)  # type: ignore
             generator = utils.SyncToAsyncIterator(generator, self.limiter)
-        async for response in generator:
-            yield self._process_example(message, response)
+        async with aclosing(generator):
+            async for response in generator:
+                yield self._process_example(message, response)

     def _pop_last_user_message(
         self,
diff --git a/gradio/utils.py b/gradio/utils.py
index b243bf1bf8..2cf7f35585 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -867,7 +867,7 @@ async def __anext__(self):
             run_sync_iterator_async, self.iterator, limiter=self.limiter
         )

-    def aclose(self):
+    async def aclose(self):
         self.iterator.close()


@@ -1939,7 +1939,7 @@ async def safe_aclose_iterator(iterator, timeout=60.0, retry_interval=0.05):
     if isinstance(iterator, SyncToAsyncIterator):
         while True:
             try:
-                iterator.aclose()
+                await iterator.aclose()
                 break
             except ValueError as e:
                 if "already executing" in str(e):
@@ -1949,7 +1949,7 @@ async def safe_aclose_iterator(iterator, timeout=60.0, retry_interval=0.05):
                 else:
                     raise
     else:
-        iterator.aclose()
+        await iterator.aclose()


 def set_default_buttons(

PATCH
