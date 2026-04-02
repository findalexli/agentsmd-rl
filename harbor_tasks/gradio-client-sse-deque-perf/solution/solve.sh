#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency: check if already fixed
if grep -q 'popleft()' client/python/gradio_client/utils.py 2>/dev/null; then
    echo "Already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/client/python/gradio_client/client.py b/client/python/gradio_client/client.py
index d6d0e0d637..59e71ac6c5 100644
--- a/client/python/gradio_client/client.py
+++ b/client/python/gradio_client/client.py
@@ -17,6 +17,7 @@
 import urllib.parse
 import uuid
 import warnings
+from collections import deque
 from collections.abc import AsyncGenerator, Callable
 from concurrent.futures import Future
 from contextvars import copy_context
@@ -212,7 +213,7 @@ def __init__(

         self.stream_open = False
         self.streaming_future: Future | None = None
-        self.pending_messages_per_event: dict[str, list[Message | None]] = {}
+        self.pending_messages_per_event: dict[str, deque[Message | None]] = {}
         self.pending_event_ids: set[str] = set()

     def close(self):
@@ -287,7 +288,7 @@ def stream_messages(
                                     return
                                 event_id = resp["event_id"]
                                 if event_id not in self.pending_messages_per_event:
-                                    self.pending_messages_per_event[event_id] = []
+                                    self.pending_messages_per_event[event_id] = deque()
                                 self.pending_messages_per_event[event_id].append(resp)
                                 if resp["msg"] == ServerMessage.process_completed:
                                     self.pending_event_ids.remove(event_id)
@@ -1182,7 +1183,7 @@ def _predict(*data, **kwargs) -> tuple:
                     data, hash_data, self.protocol, helper.request_headers
                 )
                 self.client.pending_event_ids.add(event_id)
-                self.client.pending_messages_per_event[event_id] = []
+                self.client.pending_messages_per_event[event_id] = deque()
                 helper.event_id = event_id
                 result = self._sse_fn_v1plus(helper, event_id, self.protocol)
             else:
diff --git a/client/python/gradio_client/utils.py b/client/python/gradio_client/utils.py
index d3e4af2d2b..4a1e5c13d0 100644
--- a/client/python/gradio_client/utils.py
+++ b/client/python/gradio_client/utils.py
@@ -14,6 +14,7 @@
 import tempfile
 import time
 import warnings
+from collections import deque
 from collections.abc import Callable, Coroutine
 from dataclasses import dataclass, field
 from datetime import datetime
@@ -359,7 +360,7 @@ def get_pred_from_sse_v1plus(
     helper: Communicator,
     headers: dict[str, str],
     cookies: dict[str, str] | None,
-    pending_messages_per_event: dict[str, list[Message | None]],
+    pending_messages_per_event: dict[str, deque[Message | None]],
     event_id: str,
     protocol: Literal["sse_v1", "sse_v2", "sse_v2.1"],
     ssl_verify: bool,
@@ -483,7 +484,7 @@ def stream_sse_v0(

 def stream_sse_v1plus(
     helper: Communicator,
-    pending_messages_per_event: dict[str, list[Message | None]],
+    pending_messages_per_event: dict[str, deque[Message | None]],
     event_id: str,
     protocol: Literal["sse_v1", "sse_v2", "sse_v2.1", "sse_v3"],
 ) -> dict[str, Any]:
@@ -493,7 +494,7 @@ def stream_sse_v1plus(

         while True:
             if len(pending_messages) > 0:
-                msg = pending_messages.pop(0)
+                msg = pending_messages.popleft()
             else:
                 time.sleep(0.05)
                 continue

PATCH

echo "Patch applied successfully."
