#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for SetTitleCallbackProcessor polling time
# This increases polling time from ~3.75s to ~12s and extracts logic to _poll_for_title()
patch -p1 <<'PATCH'
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
+                'Title poll failed: %s',
+                exc,
+            )
+        else:
+            title = response.json().get('title')
+            if title:
+                return title
+
+    return None


  class SetTitleCallbackProcessor(EventCallbackProcessor):
@@ -67,29 +108,11 @@ async def __call__(
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
PATCH

# Idempotency check - verify the patch was applied
grep -q "_POLL_DELAY_S = 3" openhands/app_server/event_callback/set_title_callback_processor.py || exit 1
grep -q "async def _poll_for_title" openhands/app_server/event_callback/set_title_callback_processor.py || exit 1

# Also update the unit test to expect warning instead of debug
sed -i 's/_logger\.debug/_logger.warning/g' tests/unit/app_server/test_set_title_callback_processor.py
sed -i 's/logger_debug/logger_warning/g' tests/unit/app_server/test_set_title_callback_processor.py

echo "SetTitleCallbackProcessor fix applied successfully"
