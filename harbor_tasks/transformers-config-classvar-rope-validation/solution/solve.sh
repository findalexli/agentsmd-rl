#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if architectures is already an instance attr (not ClassVar), skip
if grep -q '^\s*architectures:\s*list\[str\]\s*|\s*None\s*=\s*None' src/transformers/configuration_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/configuration_utils.py b/src/transformers/configuration_utils.py
index 408d53e5a24a..2b259b43c2a1 100755
--- a/src/transformers/configuration_utils.py
+++ b/src/transformers/configuration_utils.py
@@ -161,6 +161,9 @@ class PreTrainedConfig(PushToHubMixin, RotaryEmbeddingConfigMixin):
             `float16` weights.
     """

+    # Class attributes that we don't want to save or have in `self.__dict__`
+    # They are not supposed to be set/changed by users. Each field is set when
+    # creating a model class
     base_config_key: ClassVar[str] = ""
     sub_configs: ClassVar[dict[str, type["PreTrainedConfig"]]] = {}
     has_no_defaults_at_init: ClassVar[bool] = False
@@ -171,10 +174,11 @@ class PreTrainedConfig(PushToHubMixin, RotaryEmbeddingConfigMixin):
     base_model_ep_plan: ClassVar[dict[str, Sequence[list[str]]] | None] = None
     _auto_class: ClassVar[str | None] = None

-    # Attributes set for all models internally when saving
+    # Attributes set internally when saving and used to infer model
+    # class for `Auto` mapping
     model_type: ClassVar[str] = ""
-    transformers_version: ClassVar[str | None] = None
-    architectures: ClassVar[list[str] | None] = None
+    transformers_version: str | None = None
+    architectures: list[str] | None = None

     # Common attributes for all models
     output_hidden_states: bool | None = False
diff --git a/src/transformers/modeling_rope_utils.py b/src/transformers/modeling_rope_utils.py
index ac17573bdbc8..db825b14a026 100644
--- a/src/transformers/modeling_rope_utils.py
+++ b/src/transformers/modeling_rope_utils.py
@@ -703,8 +703,10 @@ def validate_rope(self: "PreTrainedConfig"):
         """
         Validate the RoPE config arguments, given a `"PreTrainedConfig"` object
         """
+        # Don't validate if no rope_parameters found (`None`) or if it's an empty dict
+        # Note that validation runs every time a new config is created, even if config is non-RoPE
         rope_parameters_dict = getattr(self, "rope_parameters", None)
-        if rope_parameters_dict is None:
+        if not rope_parameters_dict:
             return

         if getattr(self, "layer_types", None) is not None and set(rope_parameters_dict.keys()).issubset(
diff --git a/src/transformers/utils/auto_docstring.py b/src/transformers/utils/auto_docstring.py
index 525998d4618d..65d5eb95e272 100644
--- a/src/transformers/utils/auto_docstring.py
+++ b/src/transformers/utils/auto_docstring.py
@@ -16,6 +16,7 @@
 import inspect
 import os
 from collections.abc import Mapping
+from dataclasses import fields
 from functools import lru_cache
 from pathlib import Path
 from types import UnionType
@@ -3256,7 +3257,15 @@ def _get_parameter_info(param_name, documented_params, source_args_dict, param_t


 def _process_regular_parameters(
-    sig, func, class_name, documented_params, indent_level, undocumented_parameters, source_args_dict, parent_class
+    sig,
+    func,
+    class_name,
+    documented_params,
+    indent_level,
+    undocumented_parameters,
+    source_args_dict,
+    parent_class,
+    allowed_params=None,
 ):
     """
     Process all regular parameters (not kwargs parameters) from the function signature.
@@ -3291,6 +3300,10 @@ def _process_regular_parameters(
         ):
             continue

+        # When a filter is active (e.g. config classes: only own annotations), skip inherited params
+        if allowed_params is not None and param_name not in allowed_params:
+            continue
+
         param_name = ARGS_TO_RENAME.get(param_name, param_name)

         # Process parameter type and optional status
@@ -3768,7 +3781,15 @@ def _add_return_tensors_to_docstring(func, parent_class, docstring, indent_level


 def _process_parameters_section(
-    func_documentation, sig, func, class_name, model_name_lowercase, parent_class, indent_level, source_args_dict
+    func_documentation,
+    sig,
+    func,
+    class_name,
+    model_name_lowercase,
+    parent_class,
+    indent_level,
+    source_args_dict,
+    allowed_params,
 ):
     """
     Process the parameters section of the docstring.
@@ -3794,7 +3815,15 @@ def _process_parameters_section(

     # Process regular parameters
     param_docstring, missing_args = _process_regular_parameters(
-        sig, func, class_name, documented_params, indent_level, undocumented_parameters, source_args_dict, parent_class
+        sig,
+        func,
+        class_name,
+        documented_params,
+        indent_level,
+        undocumented_parameters,
+        source_args_dict,
+        parent_class,
+        allowed_params,
     )
     docstring += param_docstring

@@ -4059,7 +4088,13 @@ def _process_example_section(


 def auto_method_docstring(
-    func, parent_class=None, custom_intro=None, custom_args=None, checkpoint=None, source_args_dict=None
+    func,
+    parent_class=None,
+    custom_intro=None,
+    custom_args=None,
+    checkpoint=None,
+    source_args_dict=None,
+    allowed_params=None,
 ):
     """
     Wrapper that automatically generates docstring.
@@ -4088,7 +4123,15 @@ def auto_method_docstring(

     # Process Parameters section
     docstring += _process_parameters_section(
-        func_documentation, sig, func, class_name, model_name_lowercase, parent_class, indent_level, source_args_dict
+        func_documentation,
+        sig,
+        func,
+        class_name,
+        model_name_lowercase,
+        parent_class,
+        indent_level,
+        source_args_dict,
+        allowed_params,
     )

     # Process Returns section
@@ -4171,12 +4214,22 @@ def auto_class_docstring(cls, custom_intro=None, custom_args=None, checkpoint=No
         doc_class = cls.__doc__
         if custom_args is None and doc_class:
             custom_args = doc_class
+
+        # `fields(cls)` returns only the annotations defined on cls exclduing `ClassVar`
+        # (e.g. model_type). Also exclude two quasi-ClassVar fields which can `setattr` and
+        # saved in config. These do not act as class attributes and thus cannot be `ClassVar`
+        # in its general sense.
+        own_config_params = {
+            field.name for field in fields(cls) if field.name not in ["transformers_version", "architectures"]
+        }
+        allowed_params = own_config_params if own_config_params else None
         docstring_init = auto_method_docstring(
             cls.__init__,
             parent_class=cls,
             custom_args=custom_args,
             checkpoint=checkpoint,
             source_args_dict=get_args_doc_from_source([ConfigArgs]),
+            allowed_params=allowed_params,
         ).__doc__

     indent_level = get_indent_level(cls)
diff --git a/tests/utils/test_configuration_utils.py b/tests/utils/test_configuration_utils.py
index a6d91e9ac93c..f4b1041274d4 100644
--- a/tests/utils/test_configuration_utils.py
+++ b/tests/utils/test_configuration_utils.py
@@ -144,6 +144,7 @@ def test_config_common_kwargs_is_complete(self):
         self.assertListEqual(
             missing_keys,
             [
+                "transformers_version",
                 "is_encoder_decoder",
                 "tokenizer_class",
                 "_name_or_path",
diff --git a/utils/check_config_attributes.py b/utils/check_config_attributes.py
index 01b9a3c7ecb7..dd7bb04ec182 100644
--- a/utils/check_config_attributes.py
+++ b/utils/check_config_attributes.py
@@ -143,6 +143,8 @@
 # Common and important attributes, even if they do not always appear in the modeling files (can be a regex pattern)
 ATTRIBUTES_TO_ALLOW = (
     # Attr in base `PreTrainedConfig`
+    "transformers_version",
+    "architectures",
     "chunk_size_feed_forward",
     "dtype",
     "id2label",

PATCH

echo "Patch applied successfully."
