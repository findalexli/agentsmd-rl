#!/usr/bin/env bash
# Oracle solution: applies the gold patch from PR #13980 inline.
set -euo pipefail

cd /workspace/openhands

# Idempotency guard: the patch adds `def resolve_provider_llm_base_url(`
# to openhands/app_server/config.py.  If it's already there, do nothing.
if grep -q "def resolve_provider_llm_base_url" openhands/app_server/config.py; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/enterprise/server/routes/users_v1.py b/enterprise/server/routes/users_v1.py
index 902643ade1d7..6bc7cb7e4147 100644
--- a/enterprise/server/routes/users_v1.py
+++ b/enterprise/server/routes/users_v1.py
@@ -12,7 +12,10 @@
 from server.auth.saas_user_auth import SaasUserAuth
 from server.models.user_models import SaasUserInfo

-from openhands.app_server.config import depends_user_context
+from openhands.app_server.config import (
+    depends_user_context,
+    resolve_provider_llm_base_url,
+)
 from openhands.app_server.sandbox.session_auth import validate_session_key_ownership
 from openhands.app_server.user.auth_user_context import AuthUserContext
 from openhands.app_server.user.user_context import UserContext
@@ -42,8 +45,9 @@ def _inject_sdk_compat_fields(
     """
     agent_settings = content.get('agent_settings') or {}
     llm = agent_settings.get('llm') or {}
-    content['llm_model'] = llm.get('model')
-    content['llm_base_url'] = llm.get('base_url')
+    model = llm.get('model')
+    content['llm_model'] = model
+    content['llm_base_url'] = resolve_provider_llm_base_url(model, llm.get('base_url'))
     if include_api_key:
         content['llm_api_key'] = llm.get('api_key')
     content['mcp_config'] = agent_settings.get('mcp_config')
diff --git a/openhands/app_server/app_conversation/live_status_app_conversation_service.py b/openhands/app_server/app_conversation/live_status_app_conversation_service.py
index bde771207ce8..bce1a0eab637 100644
--- a/openhands/app_server/app_conversation/live_status_app_conversation_service.py
+++ b/openhands/app_server/app_conversation/live_status_app_conversation_service.py
@@ -52,7 +52,10 @@
 from openhands.app_server.app_conversation.sql_app_conversation_info_service import (
     SQLAppConversationInfoService,
 )
-from openhands.app_server.config import get_event_callback_service
+from openhands.app_server.config import (
+    get_event_callback_service,
+    resolve_provider_llm_base_url,
+)
 from openhands.app_server.errors import SandboxError
 from openhands.app_server.event.event_service import EventService
 from openhands.app_server.event_callback.event_callback_models import EventCallback
@@ -890,24 +893,12 @@ def _configure_llm(self, user: UserInfo, llm_model: str | None) -> LLM:
             or user.agent_settings.llm.model
             or LLM.model_fields['model'].default
         )
-        base_url = user.agent_settings.llm.base_url
-        if model and (
-            model.startswith('openhands/') or model.startswith('litellm_proxy/')
-        ):
-            # The SDK auto-fills base_url with the default public proxy for
-            # openhands/ models.  We need to distinguish "user explicitly set a
-            # custom URL" from "SDK auto-filled the default".
-            #
-            # Priority: user-explicit URL > deployment provider URL > SDK default
-            _SDK_DEFAULT_PROXY = 'https://llm-proxy.app.all-hands.dev/'
-            user_set_custom = base_url and base_url.rstrip(
-                '/'
-            ) != _SDK_DEFAULT_PROXY.rstrip('/')
-            if user_set_custom:
-                pass  # keep user's explicit base_url
-            elif self.openhands_provider_base_url:
-                base_url = self.openhands_provider_base_url
-            # else: keep the SDK default
+
+        base_url = resolve_provider_llm_base_url(
+            model,
+            user.agent_settings.llm.base_url,
+            provider_base_url=self.openhands_provider_base_url,
+        )

         return LLM(
             model=model,
diff --git a/openhands/app_server/config.py b/openhands/app_server/config.py
index d081dce40a15..cb661582421f 100644
--- a/openhands/app_server/config.py
+++ b/openhands/app_server/config.py
@@ -112,6 +112,50 @@ def get_openhands_provider_base_url() -> str | None:
     return os.getenv('OPENHANDS_PROVIDER_BASE_URL') or os.getenv('LLM_BASE_URL') or None


+# The SDK auto-fills this URL as the default for openhands/ and litellm_proxy/
+# models.  Deployments (e.g. staging) may use a different LLM proxy, configured
+# via OPENHANDS_PROVIDER_BASE_URL.
+_SDK_DEFAULT_PROXY = 'https://llm-proxy.app.all-hands.dev/'
+
+
+def resolve_provider_llm_base_url(
+    model: str | None,
+    base_url: str | None,
+    provider_base_url: str | None = None,
+) -> str | None:
+    """Apply deployment-specific LLM proxy override when needed.
+
+    When the model uses ``openhands/`` or ``litellm_proxy/`` prefix and the
+    stored ``base_url`` is the SDK default, replace it with the deployment's
+    provider URL.
+
+    Priority: user-explicit URL > deployment provider URL > SDK default.
+
+    Args:
+        model: LLM model name (e.g. ``litellm_proxy/gpt-4``).
+        base_url: The base URL from user/org settings.
+        provider_base_url: Deployment provider URL.  Falls back to
+            ``get_openhands_provider_base_url()`` when *None*.
+    """
+    if not model or not (
+        model.startswith('openhands/') or model.startswith('litellm_proxy/')
+    ):
+        return base_url
+
+    user_set_custom = base_url and base_url.rstrip('/') != _SDK_DEFAULT_PROXY.rstrip(
+        '/'
+    )
+    if user_set_custom:
+        return base_url
+
+    if provider_base_url is None:
+        provider_base_url = get_openhands_provider_base_url()
+    if provider_base_url:
+        return provider_base_url
+
+    return base_url
+
+
 def _get_default_lifespan():
     # Check legacy parameters for saas mode. If we are in SAAS mode do not apply
     # OpenHands alembic migrations
PATCH

echo "Patch applied successfully."
