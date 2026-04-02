#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency: check if already fixed (orig_func captured outside closure)
if grep -q 'orig_func = setup\.__func__' python/sglang/test/test_utils.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/test/test_utils.py b/python/sglang/test/test_utils.py
index 44f4e010ace6..6c6c29be7eaf 100644
--- a/python/sglang/test/test_utils.py
+++ b/python/sglang/test/test_utils.py
@@ -2068,9 +2068,11 @@ def __init_subclass__(cls, **kwargs):
         if getattr(setup, "_safe_setup_wrapped", False):
             return

-        def safe_setUpClass(klass, _orig=setup):
+        orig_func = setup.__func__
+
+        def safe_setUpClass(klass):
             try:
-                _orig.__func__(klass)
+                orig_func(klass)
             except Exception:
                 # Best-effort cleanup; suppress teardown errors so the
                 # original setUpClass exception propagates clearly.

PATCH

echo "Patch applied successfully."
