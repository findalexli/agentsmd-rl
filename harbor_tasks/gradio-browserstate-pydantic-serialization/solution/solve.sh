#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied (check for model_dump in browser_state.py)
grep -q 'model_dump' gradio/components/browser_state.py && exit 0

git apply - <<'PATCH'
diff --git a/gradio/components/browser_state.py b/gradio/components/browser_state.py
index d2b2d3dd9e..6ee26f006c 100644
--- a/gradio/components/browser_state.py
+++ b/gradio/components/browser_state.py
@@ -7,11 +7,24 @@
 from typing import Any

 from gradio_client.documentation import document
+from pydantic import BaseModel as PydanticBaseModel

 from gradio.components.base import Component
 from gradio.events import Events


+def _to_json_serializable(value: Any) -> Any:
+    """Convert a value to a JSON-serializable form.
+
+    Pydantic BaseModel instances are converted to dicts via model_dump(),
+    since they cannot be directly serialized by orjson and would otherwise
+    fall back to str() representation.
+    """
+    if isinstance(value, PydanticBaseModel):
+        return value.model_dump()
+    return value
+
+
 @document()
 class BrowserState(Component):
     EVENTS = [Events.change]
@@ -34,7 +47,7 @@ class BrowserState(Component):
             secret: the secret key to use for encryption. If None, a random key will be generated (recommended).
             render: should always be True, is included for consistency with other components.
         """
-        self.default_value = default_value
+        self.default_value = _to_json_serializable(default_value)
         self.secret = secret or "".join(
             secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
         )
@@ -61,9 +74,9 @@ class BrowserState(Component):
         Parameters:
             value: Value to store in local storage
         Returns:
-            Passes value through unchanged
+            Passes value through unchanged, converting Pydantic models to dicts
         """
-        return value
+        return _to_json_serializable(value)

     def api_info(self) -> dict[str, Any]:
         return {"type": {}, "description": "any json-serializable value"}

PATCH
