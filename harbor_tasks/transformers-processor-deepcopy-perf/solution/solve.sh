#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Idempotent: check if patch is already applied
if grep -q 'tokenizer_attributes' src/transformers/processing_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn - <<'PATCH'
diff --git a/src/transformers/processing_utils.py b/src/transformers/processing_utils.py
index 07ca999b6452..5f9f685cef49 100644
--- a/src/transformers/processing_utils.py
+++ b/src/transformers/processing_utils.py
@@ -704,7 +704,16 @@ def to_dict(self) -> dict[str, Any]:
         Returns:
             `dict[str, Any]`: Dictionary of all the attributes that make up this processor instance.
         """
-        output = copy.deepcopy(self.__dict__)
+        # Exclude tokenizer attributes before deepcopying to avoid copying large vocab/token structures.
+        tokenizer_attributes = set()
+        for attribute in self.__class__.get_attributes():
+            if attribute in self.__dict__:
+                modality = _get_modality_for_attribute(attribute)
+                if modality == "tokenizer":
+                    tokenizer_attributes.add(attribute)
+
+        dict_to_copy = {k: v for k, v in self.__dict__.items() if k not in tokenizer_attributes}
+        output = copy.deepcopy(dict_to_copy)

         # Get the kwargs in `__init__`.
         sig = inspect.signature(self.__init__)
@@ -714,14 +723,6 @@ def to_dict(self) -> dict[str, Any]:
         # extra attributes to be kept
         attrs_to_save += ["auto_map"]

-        # Remove tokenizers from output - they have their own vocab files and are saved separately.
-        # All other sub-processors (image_processor, feature_extractor, etc.) are kept in processor_config.json.
-        for attribute in self.__class__.get_attributes():
-            if attribute in output:
-                modality = _get_modality_for_attribute(attribute)
-                if modality == "tokenizer":
-                    del output[attribute]
-
         if "chat_template" in output:
             del output["chat_template"]

PATCH
