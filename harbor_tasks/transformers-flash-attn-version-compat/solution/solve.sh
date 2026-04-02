#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already applied
if grep -q 'is_flash_attn_greater_or_equal_2_10' src/transformers/utils/import_utils.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/utils/__init__.py b/src/transformers/utils/__init__.py
index 699d28c7ff04..7b8bfb80ec19 100644
--- a/src/transformers/utils/__init__.py
+++ b/src/transformers/utils/__init__.py
@@ -134,6 +134,7 @@
     is_flash_attn_3_available,
     is_flash_attn_4_available,
     is_flash_attn_greater_or_equal,
+    is_flash_attn_greater_or_equal_2_10,
     is_flute_available,
     is_fouroversix_available,
     is_fp_quant_available,
diff --git a/src/transformers/utils/import_utils.py b/src/transformers/utils/import_utils.py
index e7a3068fe403..6d9cef86e499 100644
--- a/src/transformers/utils/import_utils.py
+++ b/src/transformers/utils/import_utils.py
@@ -25,6 +25,7 @@
 import shutil
 import subprocess
 import sys
+import warnings
 from collections import OrderedDict
 from collections.abc import Callable
 from enum import Enum
@@ -973,6 +974,16 @@ def is_flash_attn_greater_or_equal(library_version: str) -> bool:
         return False


+@lru_cache
+def is_flash_attn_greater_or_equal_2_10() -> bool:
+    warnings.warn(
+        "`is_flash_attn_greater_or_equal_2_10` is deprecated and will be removed in v5.8. "
+        "Please use `is_flash_attn_greater_or_equal(library_version='2.1.0')` instead if needed.",
+        FutureWarning,
+    )
+    return is_flash_attn_greater_or_equal("2.1.0")
+
+
 @lru_cache
 def is_huggingface_hub_greater_or_equal(library_version: str, accept_dev: bool = False) -> bool:
     is_available, hub_version = _is_package_available("huggingface_hub", return_version=True)

PATCH

echo "Patch applied successfully."
