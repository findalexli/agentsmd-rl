#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for adding log fields (module, funcName, lineno)
cat <<'PATCH' | git apply -
diff --git a/enterprise/server/logger.py b/enterprise/server/logger.py
index 50a502240688..7f33325f91d6 100644
--- a/enterprise/server/logger.py
+++ b/enterprise/server/logger.py
@@ -80,8 +80,7 @@ def setup_json_logger(
     handler.setLevel(level)

     formatter = JsonFormatter(
-        '{message}{levelname}',
-        style='{',
+        '%(message)s%(levelname)s%(module)s%(funcName)s%(lineno)d',
         rename_fields={'levelname': 'severity'},
         json_serializer=custom_json_serializer,
         # Use 'ts' for consistency with LOG_JSON_FOR_CONSOLE mode (skip when console mode to avoid duplicates)
PATCH

# Idempotency check: verify the fix was applied
grep -q "%(module)s%(funcName)s%(lineno)d" enterprise/server/logger.py && echo "Patch applied successfully"
