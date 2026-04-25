#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for PR #13638
# Fix: planning agent auth error due to missing base_url
# Adds litellm_proxy/ prefix check alongside openhands/ in _configure_llm

patch -p1 << 'PATCH'
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

# Verify the patch was applied
grep -q "litellm_proxy/" openhands/app_server/app_conversation/live_status_app_conversation_service.py && \
    echo "Patch applied successfully: litellm_proxy/ prefix check added"
