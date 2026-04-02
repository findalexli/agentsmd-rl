#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if heartbeat_task.cancel() is already present, skip
if grep -q 'heartbeat_task\.cancel()' gradio/routes.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/routes.py b/gradio/routes.py
index dcab1ae0a5..4def1cf6ad 100644
--- a/gradio/routes.py
+++ b/gradio/routes.py
@@ -1514,11 +1514,12 @@ async def heartbeat():
                         await queue.put(HeartbeatMessage())

             async def sse_stream(request: fastapi.Request):
+                heartbeat_task = asyncio.create_task(heartbeat())
                 try:
-                    asyncio.create_task(heartbeat())
                     while True:
                         if await request.is_disconnected():
                             await blocks._queue.clean_events(session_hash=session_hash)
+                            heartbeat_task.cancel()
                             return

                         if (
@@ -1580,6 +1581,7 @@ async def sse_stream(request: fastapi.Request):
                                     response = process_msg(message)
                                     if response is not None:
                                         yield response
+                                    heartbeat_task.cancel()
                                     return
                 except BaseException as e:
                     message = UnexpectedErrorMessage(
@@ -1592,6 +1594,7 @@ async def sse_stream(request: fastapi.Request):
                         await blocks._queue.clean_events(session_hash=session_hash)
                     if response is not None:
                         yield response
+                    heartbeat_task.cancel()
                     raise e

             return StreamingResponse(

PATCH

echo "Patch applied successfully."
