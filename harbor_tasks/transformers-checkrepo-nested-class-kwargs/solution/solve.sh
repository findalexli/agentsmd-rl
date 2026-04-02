#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

TARGET="utils/check_repo.py"

# Idempotency: check if fix is already applied
if grep -q '@functools.lru_cache' "$TARGET" 2>/dev/null; then
    echo "Fix already applied (lru_cache found)."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/utils/check_repo.py b/utils/check_repo.py
index 081accf68264..3ed1bb0abc12 100644
--- a/utils/check_repo.py
+++ b/utils/check_repo.py
@@ -31,6 +31,7 @@
 """

 import ast
+import functools
 import os
 import re
 import types
@@ -565,6 +566,7 @@ def check_model_list():

 # If some modeling modules should be ignored for all checks, they should be added in the nested list
 # _ignore_modules of this function.
+@functools.lru_cache(maxsize=1)
 def get_model_modules() -> list[str]:
     """Get all the model modules inside the transformers library (except deprecated models)."""
     _ignore_modules = [
@@ -1339,11 +1341,11 @@ def check_models_have_kwargs():
             with open(modeling_file, "r", encoding="utf-8") as f:
                 tree = ast.parse(f.read())

-            # Map all classes in the file to their base classes
+            # Map all classes in the file to their base classes (only top-level classes)
             class_bases = {}
             all_class_nodes = {}

-            for node in ast.walk(tree):
+            for node in tree.body:
                 if isinstance(node, ast.ClassDef):
                     # We only care about base classes that are simple names
                     bases = [b.id for b in node.bases if isinstance(b, ast.Name)]

PATCH

echo "Patch applied successfully."
