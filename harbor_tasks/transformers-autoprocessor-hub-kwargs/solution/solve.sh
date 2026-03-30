#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

cat > /tmp/patch.diff << 'PATCH'
diff --git a/src/transformers/models/auto/processing_auto.py b/src/transformers/models/auto/processing_auto.py
index 834a04541ed8..0bfdc61e7405 100644
--- a/src/transformers/models/auto/processing_auto.py
+++ b/src/transformers/models/auto/processing_auto.py
@@ -14,7 +14,6 @@
 """AutoProcessor class."""

 import importlib
-import inspect
 import json
 from collections import OrderedDict
 from typing import TYPE_CHECKING
@@ -297,7 +296,18 @@ def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):

         # First, let's see if we have a processor or preprocessor config.
         # Filter the kwargs for `cached_file`.
-        cached_file_kwargs = {key: kwargs[key] for key in inspect.signature(cached_file).parameters if key in kwargs}
+        _hub_valid_kwargs = (
+            "cache_dir",
+            "force_download",
+            "proxies",
+            "token",
+            "revision",
+            "local_files_only",
+            "subfolder",
+            "repo_type",
+            "user_agent",
+        )
+        cached_file_kwargs = {key: kwargs[key] for key in _hub_valid_kwargs if key in kwargs}
         # We don't want to raise
         cached_file_kwargs.update(
             {
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
