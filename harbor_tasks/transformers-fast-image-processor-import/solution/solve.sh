#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Idempotent: check if patch is already applied
if grep -q '_proc_file' src/transformers/__init__.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn - <<'PATCH'
diff --git a/src/transformers/__init__.py b/src/transformers/__init__.py
index 06d6f7931467..b6ba58e2e301 100755
--- a/src/transformers/__init__.py
+++ b/src/transformers/__init__.py
@@ -822,6 +822,28 @@ def _get_target():
     _create_module_alias(f"{__name__}.tokenization_utils", ".tokenization_utils_sentencepiece")
     _create_module_alias(f"{__name__}.image_processing_utils_fast", ".image_processing_backends")

+    for _proc_file in sorted((Path(__file__).parent / "models").rglob("image_processing_*.py")):
+        _model = _proc_file.parent.name
+        _module = _proc_file.stem
+        _target = f".models.{_model}.{_module}"
+        _create_module_alias(f"{__name__}.models.{_model}.{_module}_fast", _target)
+
+        # Also map XImageProcessorFast -> XImageProcessor for backward compat with old class names.
+        def getattr_factory(target):
+            def _getattr(name):
+                new_name = name.removesuffix("Fast")
+                logger.warning(
+                    "Accessing `%s` from `%s`. Returning `%s` instead. Behavior may be "
+                    "different and this alias will be removed in future versions.",
+                    name,
+                    target,
+                    new_name,
+                )
+                return getattr(importlib.import_module(target, __name__), new_name)
+
+            return _getattr
+
+        sys.modules[f"{__name__}.models.{_model}.{_module}_fast"].__getattr__ = getattr_factory(_target)

 if not is_torch_available():
     logger.warning_advice(
diff --git a/utils/check_repo.py b/utils/check_repo.py
index 73aa08b20d50..081accf68264 100644
--- a/utils/check_repo.py
+++ b/utils/check_repo.py
@@ -1191,6 +1191,9 @@ def ignore_undocumented(name: str) -> bool:
     # BLT models are internal building blocks, tested implicitly through BltForCausalLM
     if name.startswith("Blt"):
         return True
+    # image_processing_*_fast are backward-compat module aliases, not public objects.
+    if name.startswith("image_processing_") and name.endswith("_fast"):
+        return True
     if name in SHOULD_HAVE_THEIR_OWN_PAGE:
         return True
     return False
PATCH
