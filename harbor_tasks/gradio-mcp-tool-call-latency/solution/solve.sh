#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied
grep -q 'process_api' gradio/mcp.py && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/gradio/mcp.py b/gradio/mcp.py
index 2e4f874e8f..849cc4a554 100644
--- a/gradio/mcp.py
+++ b/gradio/mcp.py
@@ -28,6 +28,7 @@
 from gradio.blocks import BlockFunction
 from gradio.components import State
 from gradio.route_utils import Header
+from gradio.state_holder import SessionState

 if TYPE_CHECKING:
     from mcp import types  # noqa: F401
@@ -326,7 +327,7 @@ def _format_progress_message(update: StatusUpdate) -> str | None:
         return None

     async def _execute_tool_with_progress(  # type: ignore
-        self, job: Any, progress_token: str
+        self, job: Any, progress_token: str | int
     ) -> dict[str, Any]:
         """
         Execute a tool call with progress tracking (streaming path).
@@ -394,27 +395,46 @@ async def call_tool(
                 name: The name of the tool to call.
                 arguments: The arguments to pass to the tool.
             """
-            progress_token = None
-            if self.mcp_server.request_context.meta is not None:
-                progress_token = self.mcp_server.request_context.meta.progressToken
-
-            client = await run_sync(self._get_or_create_client)
             endpoint_name, processed_args, request_headers, block_fn = (
                 self._prepare_tool_call_args(name, arguments)
             )
             processed_args = self.insert_empty_state(block_fn.inputs, processed_args)
-            job = client.submit(
-                *processed_args, api_name=endpoint_name, headers=request_headers
-            )

-            if progress_token is None or not block_fn.queue:
-                output_data = await self._execute_tool_without_progress(job)
+            if not block_fn.queue:
+                # Fast path for non-queued events: call blocks.process_api()
+                # directly instead of the HTTP loopback through gradio_client.
+                # This eliminates thread dispatches, TCP round-trips, and SSE
+                # overhead — reducing MCP tool-call latency significantly.
+                session_state = SessionState(self.blocks)
+                raw_output = await self.blocks.process_api(
+                    block_fn=block_fn,
+                    inputs=processed_args,
+                    state=session_state,
+                    request=self.mcp_server.request_context.request,
+                )
+                output_data = raw_output["data"]
             else:
-                output_data = await self._execute_tool_with_progress(  # type: ignore
-                    job,
-                    progress_token,  # type: ignore
+                # Queued path: use the HTTP loopback to preserve streaming
+                # updates, progress notifications, and queue-based features.
+                progress_token = None
+                if self.mcp_server.request_context.meta is not None:
+                    progress_token = self.mcp_server.request_context.meta.progressToken
+
+                client = await run_sync(self._get_or_create_client)
+                job = client.submit(
+                    *processed_args,
+                    api_name=endpoint_name,
+                    headers=request_headers,
                 )

+                if progress_token is None:
+                    output_data = await self._execute_tool_without_progress(job)
+                else:
+                    output_data = await self._execute_tool_with_progress(
+                        job,
+                        progress_token,
+                    )
+
             output_data = self.pop_returned_state(block_fn.outputs, output_data)

             context_request: Request | None = self.mcp_server.request_context.request

PATCH
