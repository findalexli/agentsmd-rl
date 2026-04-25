#!/bin/bash
set -e

cd /workspace/openhands

# Apply the fix for planning agent auth error
# The _configure_llm method needs to check for both 'openhands/' and 'litellm_proxy/' prefixes

cat <<'PATCH' | git apply -
diff --git a/openhands/app_server/app_conversation/live_status_app_conversation_service.py b/openhands/app_server/app_conversation/live_status_app_conversation_service.py
index b2dbda588200..f3010ad40628 100644
--- a/openhands/app_server/app_conversation/live_status_app_conversation_service.py
+++ b/openhands/app_server/app_conversation/live_status_app_conversation_service.py
@@ -890,7 +890,9 @@ def _configure_llm(self, user: UserInfo, llm_model: str | None) -> LLM:
         """
         model = llm_model or user.llm_model
         base_url = user.llm_base_url
-        if model and model.startswith('openhands/'):
+        if model and (
+            model.startswith('openhands/') or model.startswith('litellm_proxy/')
+        ):
             base_url = user.llm_base_url or self.openhands_provider_base_url

         return LLM(
PATCH

echo "Applied fix: litellm_proxy/ prefix now recognized in _configure_llm"
