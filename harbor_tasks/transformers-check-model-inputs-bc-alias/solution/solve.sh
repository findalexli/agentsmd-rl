#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency: skip if already applied
if grep -q 'def check_model_inputs' src/transformers/utils/generic.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/utils/generic.py b/src/transformers/utils/generic.py
index d77aa0c156eb..4a9536d74b91 100644
--- a/src/transformers/utils/generic.py
+++ b/src/transformers/utils/generic.py
@@ -940,6 +940,14 @@ def wrapper(self, *args, **kwargs):
     return wrapper


+# bc for check_model_inputs:
+
+
+def check_model_inputs(func):
+    logger.warning_once("The `check_model_inputs` decorator is deprecated in favor of `merge_with_config_defaults`.")
+    return merge_with_config_defaults(func)
+
+
 class GeneralInterface(MutableMapping):
     """
      Dict-like object keeping track of a class-wide mapping, as well as a local one. Allows to have library-wide

PATCH

echo "Patch applied successfully."
