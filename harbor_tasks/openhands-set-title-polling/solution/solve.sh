#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already patched (idempotency check)
if grep -q "_POLL_DELAY_S = 3" openhands/app_server/event_callback/set_title_callback_processor.py; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/openhands/app_server/event_callback/set_title_callback_processor.py b/openhands/app_server/event_callback/set_title_callback_processor.py
index 37d70370b04a..ae487f7341e1 100644
--- a/openhands/app_server/event_callback/set_title_callback_processor.py
+++ b/openhands/app_server/event_callback/set_title_callback_processor.py
@@ -25,8 +25,49 @@

 _logger = logging.getLogger(__name__)

-# Poll with ~3.75s total wait per message event before retrying later.
-_TITLE_POLL_DELAYS_S = (0.25, 0.5, 1.0, 2.0)
+# Delay between attempts to poll title
+_POLL_DELAY_S = 3
+# Number of attempts to poll title
+_NUM_POLL_ATTEMPTS = 4
+
+
+async def _poll_for_title(
+    httpx_client: httpx.AsyncClient,
+    url: str,
+    session_api_key: str | None,
+) -> str | None:
+    """Poll the agent server for the conversation title.
+
+    Args:
+        httpx_client: The HTTP client to use for requests.
+        url: The conversation URL to poll.
+        session_api_key: The session API key for authentication.
+
+    Returns:
+        The title if available, None otherwise.
+    """
+    for _ in range(_NUM_POLL_ATTEMPTS):
+        await asyncio.sleep(_POLL_DELAY_S)
+        try:
+            response = await httpx_client.get(
+                url,
+                headers={
+                    'X-Session-API-Key': session_api_key,
+                },
+            )
+            response.raise_for_status()
+        except httpx.HTTPError as exc:
+            # Transient agent-server failures are acceptable; retry later.
+            _logger.warning(
+                'Title poll failed for conversation %s: %s',
+                exc,
+            )
+        else:
+            title = response.json().get('title')
+            if title:
+                return title
+
+    return None


 class SetTitleCallbackProcessor(EventCallbackProcessor):
@@ -67,29 +108,11 @@ class SetTitleCallbackProcessor(EventCallbackProcessor):
                 app_conversation_url
             )

-            title = None
-            for delay_s in _TITLE_POLL_DELAYS_S:
-                try:
-                    response = await httpx_client.get(
-                        app_conversation_url,
-                        headers={
-                            'X-Session-API-Key': app_conversation.session_api_key,
-                        },
-                    )
-                    response.raise_for_status()
-                except httpx.HTTPError as exc:
-                    # Transient agent-server failures are acceptable; retry later.
-                    _logger.debug(
-                        'Title poll failed for conversation %s: %s',
-                        conversation_id,
-                        exc,
-                    )
-                else:
-                    title = response.json().get('title')
-                    if title:
-                        break
-                # Backoff applies to both missing-title responses and transient errors.
-                await asyncio.sleep(delay_s)
+            title = await _poll_for_title(
+                httpx_client,
+                app_conversation_url,
+                app_conversation.session_api_key,
+            )

             if not title:
                 # Keep the callback active so later message events can retry.
diff --git a/tests/unit/app_server/test_set_title_callback_processor.py b/tests/unit/app_server/test_set_title_callback_processor.py
index 2c992be3f901..ef0257be826f 100644
--- a/tests/unit/app_server/test_set_title_callback_processor.py
+++ b/tests/unit/app_server/test_set_title_callback_processor.py
@@ -281,14 +281,14 @@ def get_httpx_client(_state):
         ),
         patch(
             'openhands.app_server.event_callback.'
-            'set_title_callback_processor._logger.debug'
-        ) as logger_debug,
+            'set_title_callback_processor._logger.warning'
+        ) as logger_warning,
     ):
         result = await processor(conversation_id, callback, event)

     assert result is None
     assert len(httpx_client.calls) == 4
-    assert logger_debug.call_count == 4
+    assert logger_warning.call_count == 4
     app_conversation_info_service.save_app_conversation_info.assert_not_called()
     event_callback_service.save_event_callback.assert_not_called()
     assert callback.status == EventCallbackStatus.ACTIVE
PATCH

echo "Patch applied successfully!"
