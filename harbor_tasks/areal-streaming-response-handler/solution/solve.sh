#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

FILE="areal/experimental/openai/proxy/proxy_rollout_server.py"

# Idempotent: skip if already applied
grep -q 'kwargs\.pop("stream", None)' "$FILE" && exit 0

git apply - <<'PATCH'
diff --git a/areal/experimental/openai/proxy/proxy_rollout_server.py b/areal/experimental/openai/proxy/proxy_rollout_server.py
index c7fe8e2d2..2ae74b813 100644
--- a/areal/experimental/openai/proxy/proxy_rollout_server.py
+++ b/areal/experimental/openai/proxy/proxy_rollout_server.py
@@ -586,7 +586,11 @@ def _is_default_value(k: str, v: Any) -> bool:
         kwargs["top_p"] = 1.0
         _warn_once("top_p not set in request, defaulting to 1.0")

-    # Add stream parameter if requested
+    # Strip stream from request body to prevent it from bypassing the explicit
+    # `stream` parameter.  Without this, a request with {"stream": true} would
+    # leak through kwargs and cause the client to return an AsyncGenerator even
+    # when the caller did not ask for streaming.
+    kwargs.pop("stream", None)
     if stream:
         kwargs["stream"] = True

@@ -601,16 +605,61 @@ def _is_default_value(k: str, v: Any) -> bool:
 @app.post(
     f"/{CHAT_COMPLETIONS_PATHNAME}",
     dependencies=[Depends(validate_json_request)],
+    response_model=None,
 )
 async def chat_completions(
     request: CompletionCreateParams, session_id: str = Depends(_require_session_key)
-) -> ChatCompletion:
-    """OpenAI-compatible chat completions endpoint."""
+) -> ChatCompletion | StreamingResponse:
+    """OpenAI-compatible chat completions endpoint.
+
+    Supports both streaming (stream=True) and non-streaming requests.
+    For streaming requests, returns a StreamingResponse with Server-Sent Events
+    in the OpenAI streaming format (data: {json}\\n\\n ... data: [DONE]\\n\\n).
+    """
     if _openai_client is None:
         raise HTTPException(
             status_code=500,
             detail='Proxy server not initialized. Send requests to /create_engine then /call "initialize" first.',
         )
+
+    # CompletionCreateParams is a TypedDict (dict subclass), so use dict access.
+    is_streaming = request.get("stream") is True
+
+    if is_streaming:
+        openai_stream = None
+        try:
+            openai_stream = await _call_client_create(
+                create_fn=_openai_client.chat.completions.create,
+                request=request,
+                session_id=session_id,
+                stream=True,
+            )
+
+            # Convert ChatCompletionChunk objects to OpenAI SSE format
+            async def _openai_sse_generator(
+                chunk_stream: AsyncGenerator[ChatCompletionChunk, None],
+            ) -> AsyncGenerator[str, None]:
+                async for chunk in chunk_stream:
+                    yield f"data: {chunk.model_dump_json()}\n\n"
+                yield "data: [DONE]\n\n"
+
+            safe_stream = _safe_stream_wrapper(_openai_sse_generator(openai_stream))
+
+            return StreamingResponse(
+                safe_stream,
+                media_type="text/event-stream",
+                headers={
+                    "Cache-Control": "no-cache",
+                    "Connection": "keep-alive",
+                    "X-Accel-Buffering": "no",
+                },
+            )
+        except Exception as e:
+            if openai_stream is not None and hasattr(openai_stream, "aclose"):
+                await openai_stream.aclose()
+            logger.error(f"Error setting up streaming response: {e}")
+            raise HTTPException(status_code=500, detail=f"Streaming setup failed: {e}")
+
     return await _call_client_create(
         create_fn=_openai_client.chat.completions.create,
         request=request,
PATCH
