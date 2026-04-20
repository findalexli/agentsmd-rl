#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for credential leak in callback event logging
cat <<'PATCH' | git apply -
diff --git a/openhands/app_server/event_callback/event_callback_models.py b/openhands/app_server/event_callback/event_callback_models.py
index 8b1abd6aa5af..c032977b06e1 100644
--- a/openhands/app_server/event_callback/event_callback_models.py
+++ b/openhands/app_server/event_callback/event_callback_models.py
@@ -22,6 +22,9 @@
     get_known_concrete_subclasses,
 )

+# TODO(OpenHands/evaluation#418): import from openhands.sdk.utils.redact
+from openhands.utils._redact_compat import redact_text_secrets
+
 _logger = logging.getLogger(__name__)
 if TYPE_CHECKING:
     EventKind = str
@@ -56,7 +59,11 @@ async def __call__(
         callback: EventCallback,
         event: Event,
     ) -> EventCallbackResult:
-        _logger.info(f'Callback {callback.id} Invoked for event {event}')
+        _logger.info(
+            'Callback %s Invoked for event %s',
+            callback.id,
+            redact_text_secrets(str(event)),
+        )
         return EventCallbackResult(
             status=EventCallbackResultStatus.SUCCESS,
             event_callback_id=callback.id,
diff --git a/openhands/app_server/event_callback/set_title_callback_processor.py b/openhands/app_server/event_callback/set_title_callback_processor.py
index ae487f7341e1..3251d048ae24 100644
--- a/openhands/app_server/event_callback/set_title_callback_processor.py
+++ b/openhands/app_server/event_callback/set_title_callback_processor.py
@@ -23,6 +23,9 @@
 )
 from openhands.sdk import Event, MessageEvent

+# TODO(OpenHands/evaluation#418): import from openhands.sdk.utils.redact
+from openhands.utils._redact_compat import redact_text_secrets
+
 _logger = logging.getLogger(__name__)

 # Delay between attempts to poll title
@@ -88,7 +91,11 @@ async def __call__(
             get_httpx_client,
         )

-        _logger.info(f'Callback {callback.id} Invoked for event {event}')
+        _logger.info(
+            'Callback %s Invoked for event %s',
+            callback.id,
+            redact_text_secrets(str(event)),
+        )

         state = InjectorState()
         setattr(state, USER_CONTEXT_ATTR, ADMIN)
diff --git a/openhands/utils/_redact_compat.py b/openhands/utils/_redact_compat.py
new file mode 100644
index 000000000000..34472d2a941f
--- /dev/null
+++ b/openhands/utils/_redact_compat.py
@@ -0,0 +1,168 @@
+# TODO(OpenHands/evaluation#418): Delete this file and import directly from
+# openhands.sdk.utils.redact once openhands-sdk >1.16.1 is released.
+# These functions are copied from the SDK's redact.py to unblock PRs while
+# waiting for the next SDK release.
+#
+# Source of truth: openhands-sdk/openhands/sdk/utils/redact.py
+#   in repo: https://github.com/OpenHands/software-agent-sdk
+
+import copy
+import re
+from typing import Any
+from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
+
+from openhands.sdk.utils.redact import sanitize_dict
+
+# ---------------------------------------------------------------------------
+# URL param redaction
+# ---------------------------------------------------------------------------
+
+SENSITIVE_URL_PARAMS = frozenset(
+    {
+        'tavilyapikey',
+        'apikey',
+        'api_key',
+        'token',
+        'access_token',
+        'secret',
+        'key',
+    }
+)
+
+
+def _is_secret_key(key: str) -> bool:
+    key_upper = key.upper()
+    return any(
+        p in key_upper
+        for p in (
+            'AUTHORIZATION',
+            'COOKIE',
+            'CREDENTIAL',
+            'KEY',
+            'PASSWORD',
+            'SECRET',
+            'SESSION',
+            'TOKEN',
+        )
+    )
+
+
+def redact_url_params(url: str) -> str:
+    """Redact sensitive query parameter values from a URL string."""
+    try:
+        parsed = urlparse(url)
+    except Exception:
+        return url
+    if not parsed.query:
+        return url
+    params = parse_qs(parsed.query, keep_blank_values=True)
+    redacted_params: dict[str, list[str]] = {}
+    for param_name, values in params.items():
+        if param_name.lower() in SENSITIVE_URL_PARAMS or _is_secret_key(param_name):
+            redacted_params[param_name] = ['<redacted>'] * len(values)
+        else:
+            redacted_params[param_name] = values
+    redacted_query = urlencode(redacted_params, doseq=True)
+    return urlunparse(parsed._replace(query=redacted_query))
+
+
+def _walk_redact_urls(obj: Any) -> Any:
+    if isinstance(obj, dict):
+        return {k: _walk_redact_urls(v) for k, v in obj.items()}
+    if isinstance(obj, list):
+        return [_walk_redact_urls(item) for item in obj]
+    if isinstance(obj, str) and '?' in obj:
+        return redact_url_params(obj)
+    return obj
+
+
+# ---------------------------------------------------------------------------
+# sanitize_config
+# ---------------------------------------------------------------------------
+
+
+def sanitize_config(config: dict[str, Any]) -> dict[str, Any]:
+    """Deep-copy a config dict, redact secret keys and URL query params."""
+    config = copy.deepcopy(config)
+    config = sanitize_dict(config)
+    config = _walk_redact_urls(config)
+    return config
+
+
+# ---------------------------------------------------------------------------
+# Text / string redaction
+# ---------------------------------------------------------------------------
+
+_API_KEY_LITERAL_RE = re.compile(
+    r'\b('
+    # OpenRouter / OpenAI / Anthropic
+    r'sk-(?:or-v1|proj|ant-(?:api|oat)\d{2})-[A-Za-z0-9_-]{20,}'
+    r'|gsk_[A-Za-z0-9]{20,}'  # GROQ
+    r'|hf_[A-Za-z0-9]{20,}'  # HuggingFace
+    r'|tgp_v1_[A-Za-z0-9_-]{20,}'  # Together AI
+    r'|ghp_[A-Za-z0-9]{20,}'  # GitHub PAT (classic)
+    r'|github_pat_[A-Za-z0-9_]{20,}'  # GitHub PAT (fine-grained)
+    r'|sk-oh-[A-Za-z0-9]{20,}'  # OpenHands session tokens
+    r'|ctx7sk-[A-Za-z0-9_-]{10,}'  # Context7 MCP keys
+    r'|cla_[A-Za-z0-9_-]{20,}'  # Claude.ai MCP tokens
+    r'|sntryu_[A-Za-z0-9]{10,}'  # Sentry tokens
+    r'|lin_api_[A-Za-z0-9]{10,}'  # Linear API tokens
+    r'|tvly-[A-Za-z0-9_-]{10,}'  # Tavily keys
+    r'|ATATT3x[A-Za-z0-9_-]{10,}'  # Jira/Atlassian tokens
+    r'|xoxb-[A-Za-z0-9_-]{20,}'  # Slack bot tokens
+    r'|xoxp-[A-Za-z0-9_-]{20,}'  # Slack user tokens
+    r'|Bearer\s+[A-Za-z0-9_.-]{20,}'  # Bearer tokens
+    r')'
+)
+
+
+def redact_api_key_literals(text: str) -> str:
+    """Replace bare API key literals from common providers with <redacted>."""
+    return _API_KEY_LITERAL_RE.sub('<redacted>', text)
+
+
+def redact_text_secrets(text: str) -> str:
+    """Redact secrets from a string representation of a config object."""
+    # api_key='...' patterns
+    text = re.sub(r"api_key='[^']*'", "api_key='<redacted>'", text)
+    text = re.sub(r'api_key="[^"]*"', 'api_key="<redacted>"', text)
+
+    # Dict entries with sensitive key names
+    text = re.sub(
+        r"('[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z_]*':\s*')[^']*(')",
+        r'\g<1><redacted>\2',
+        text,
+    )
+    text = re.sub(
+        r'("[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z_]*":\s*")[^"]*(")',
+        r'\g<1><redacted>\2',
+        text,
+    )
+
+    # URL query params
+    text = re.sub(
+        r'((?:tavilyApiKey|apiKey|api_key|token|access_token|secret|key)=)'
+        r"[^&\s'\")\]]+",
+        r'\g<1><redacted>',
+        text,
+        flags=re.IGNORECASE,
+    )
+
+    # Authorization header values
+    text = re.sub(
+        r"('Authorization':\s*')[^']*(')",
+        r'\g<1><redacted>\2',
+        text,
+    )
+
+    # X-Session-API-Key header values
+    text = re.sub(
+        r"('X-Session-API-Key':\s*')[^']*(')",
+        r'\g<1><redacted>\2',
+        text,
+    )
+
+    # Bare API key literals
+    text = redact_api_key_literals(text)
+
+    return text
PATCH

# Idempotency check: verify the fix was applied
if ! grep -q "redact_text_secrets" openhands/app_server/event_callback/event_callback_models.py; then
    echo "ERROR: Fix not applied correctly"
    exit 1
fi

echo "Fix applied successfully"
