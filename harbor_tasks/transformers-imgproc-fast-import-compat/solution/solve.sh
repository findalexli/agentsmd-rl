#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if the alias for image_processing_utils_fast is already set up
if grep -q 'image_processing_utils_fast.*image_processing_backends' src/transformers/__init__.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/__init__.py b/src/transformers/__init__.py
index 4b2190ace498..06d6f7931467 100755
--- a/src/transformers/__init__.py
+++ b/src/transformers/__init__.py
@@ -119,6 +119,7 @@
     ],
     "hf_argparser": ["HfArgumentParser"],
     "hyperparameter_search": [],
+    "image_processing_utils_fast": [],
     "image_transforms": [],
     "integrations": [
         "is_clearml_available",
@@ -798,13 +799,15 @@
         extra_objects={"__version__": __version__},
     )

-    def _create_tokenization_alias(alias: str, target: str) -> None:
+    def _create_module_alias(alias: str, target: str) -> None:
         """
-        Lazily redirect legacy tokenization module paths to their replacements without importing heavy deps.
+        Lazily redirect legacy module paths to their replacements without importing heavy deps.
         """
-
         module = types.ModuleType(alias)
         module.__doc__ = f"Alias module for backward compatibility with `{target}`."
+        # Set __file__ explicitly so that inspect.py's hasattr(module, '__file__') check
+        # never falls through to __getattr__ and triggers a premature (possibly circular) import.
+        module.__file__ = None

         def _get_target():
             return importlib.import_module(target, __name__)
@@ -815,8 +818,9 @@ def _get_target():
         sys.modules[alias] = module
         setattr(sys.modules[__name__], alias.rsplit(".", 1)[-1], module)

-    _create_tokenization_alias(f"{__name__}.tokenization_utils_fast", ".tokenization_utils_tokenizers")
-    _create_tokenization_alias(f"{__name__}.tokenization_utils", ".tokenization_utils_sentencepiece")
+    _create_module_alias(f"{__name__}.tokenization_utils_fast", ".tokenization_utils_tokenizers")
+    _create_module_alias(f"{__name__}.tokenization_utils", ".tokenization_utils_sentencepiece")
+    _create_module_alias(f"{__name__}.image_processing_utils_fast", ".image_processing_backends")


 if not is_torch_available():
diff --git a/src/transformers/image_processing_backends.py b/src/transformers/image_processing_backends.py
index b49aef9bd661..73b26a59d1b2 100644
--- a/src/transformers/image_processing_backends.py
+++ b/src/transformers/image_processing_backends.py
@@ -25,6 +25,7 @@
 )
 from .image_transforms import (
     convert_to_rgb,
+    divide_to_patches,  # noqa: F401 - re-exported for backward compat with image_processing_utils_fast
     get_resize_output_image_size,
     get_size_with_aspect_ratio,
     group_images_by_shape,
@@ -664,3 +665,7 @@ def to_dict(self) -> dict[str, Any]:
         if processor_dict.get("image_processor_type", "").endswith("Pil"):
             processor_dict["image_processor_type"] = processor_dict["image_processor_type"][:-3]
         return processor_dict
+
+
+# Backward-compatible alias: allow referring to TorchvisionBackend as BaseImageProcessorFast
+BaseImageProcessorFast = TorchvisionBackend

PATCH

echo "Patch applied successfully."
