#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Check if already fixed (the fix introduces a _convert_none helper)
if grep -q '_convert_none' src/prime_rl/utils/config.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/utils/config.py b/src/prime_rl/utils/config.py
index c4cf8f93be..74f24f0f0f 100644
--- a/src/prime_rl/utils/config.py
+++ b/src/prime_rl/utils/config.py
@@ -3,21 +3,24 @@
 from pydantic_config import cli  # noqa: F401


+def _convert_none(value):
+    """Recursively convert None to ``"None"`` strings for TOML serialization."""
+    if value is None:
+        return "None"
+    if isinstance(value, dict):
+        return {k: _convert_none(v) for k, v in value.items()}
+    if isinstance(value, list):
+        return [_convert_none(item) for item in value]
+    return value
+
+
 def none_to_none_str(data: dict) -> dict:
     """Convert None values to ``"None"`` strings so they survive TOML serialization.

     TOML has no null type, so we use the ``"None"`` string convention which
     ``BaseConfig._none_str_to_none`` converts back to ``None`` on load.
     """
-    out = {}
-    for key, value in data.items():
-        if value is None:
-            out[key] = "None"
-        elif isinstance(value, dict):
-            out[key] = none_to_none_str(value)
-        else:
-            out[key] = value
-    return out
+    return _convert_none(data)


 def get_all_fields(model: BaseModel | type) -> list[str]:

PATCH

echo "Patch applied successfully."
