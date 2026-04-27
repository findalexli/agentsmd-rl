#!/bin/bash
set -euo pipefail

cd /workspace/transformers

# Idempotency: if the patch is already applied, exit cleanly.
if ! grep -q "trust_remote_code" src/transformers/models/lightglue/configuration_lightglue.py 2>/dev/null; then
    if [ -f utils/mlinter/trf014.py ]; then
        echo "Gold patch already applied."
        exit 0
    fi
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/transformers/models/lightglue/configuration_lightglue.py b/src/transformers/models/lightglue/configuration_lightglue.py
index a5ee8cc3e9b7..16ef166bf001 100644
--- a/src/transformers/models/lightglue/configuration_lightglue.py
+++ b/src/transformers/models/lightglue/configuration_lightglue.py
@@ -40,8 +40,6 @@ class LightGlueConfig(PreTrainedConfig):
         The confidence threshold used to prune points
     filter_threshold (`float`, *optional*, defaults to 0.1):
         The confidence threshold used to filter matches
-    trust_remote_code (`bool`, *optional*, defaults to `False`):
-        Whether to trust remote code when using other models than SuperPoint as keypoint detector.

     Examples:
         ```python
@@ -73,10 +71,6 @@ class LightGlueConfig(PreTrainedConfig):
     hidden_act: str = "gelu"
     attention_dropout: float | int = 0.0
     attention_bias: bool = True
-    # LightGlue can be used with other models than SuperPoint as keypoint detector
-    # We provide the trust_remote_code argument to allow the use of other models
-    # that are not registered in the CONFIG_MAPPING dictionary (for example DISK)
-    trust_remote_code: bool = False

     def __post_init__(self, **kwargs):
         if self.num_key_value_heads is None:
@@ -86,14 +80,9 @@ def __post_init__(self, **kwargs):
         # See https://github.com/huggingface/transformers/pull/31718#discussion_r2109733153
         if isinstance(self.keypoint_detector_config, dict):
             self.keypoint_detector_config["model_type"] = self.keypoint_detector_config.get("model_type", "superpoint")
-            if self.keypoint_detector_config["model_type"] not in CONFIG_MAPPING:
-                self.keypoint_detector_config = AutoConfig.from_pretrained(
-                    self.keypoint_detector_config["_name_or_path"], trust_remote_code=self.trust_remote_code
-                )
-            else:
-                self.keypoint_detector_config = CONFIG_MAPPING[self.keypoint_detector_config["model_type"]](
-                    **self.keypoint_detector_config, attn_implementation="eager"
-                )
+            self.keypoint_detector_config = CONFIG_MAPPING[self.keypoint_detector_config["model_type"]](
+                **self.keypoint_detector_config, attn_implementation="eager"
+            )
         elif self.keypoint_detector_config is None:
             self.keypoint_detector_config = CONFIG_MAPPING["superpoint"](attn_implementation="eager")

diff --git a/src/transformers/models/lightglue/modeling_lightglue.py b/src/transformers/models/lightglue/modeling_lightglue.py
index f3aea377356e..1c5b90e0f4fd 100644
--- a/src/transformers/models/lightglue/modeling_lightglue.py
+++ b/src/transformers/models/lightglue/modeling_lightglue.py
@@ -502,9 +502,7 @@ class LightGlueForKeypointMatching(LightGluePreTrainedModel):

     def __init__(self, config: LightGlueConfig):
         super().__init__(config)
-        self.keypoint_detector = AutoModelForKeypointDetection.from_config(
-            config.keypoint_detector_config, trust_remote_code=config.trust_remote_code
-        )
+        self.keypoint_detector = AutoModelForKeypointDetection.from_config(config.keypoint_detector_config)

         self.keypoint_detector_descriptor_dim = config.keypoint_detector_config.descriptor_decoder_dim
         self.descriptor_dim = config.descriptor_dim
diff --git a/src/transformers/models/lightglue/modular_lightglue.py b/src/transformers/models/lightglue/modular_lightglue.py
index 701d0017ec98..62082b678b00 100644
--- a/src/transformers/models/lightglue/modular_lightglue.py
+++ b/src/transformers/models/lightglue/modular_lightglue.py
@@ -53,8 +53,6 @@ class LightGlueConfig(PreTrainedConfig):
         The confidence threshold used to prune points
     filter_threshold (`float`, *optional*, defaults to 0.1):
         The confidence threshold used to filter matches
-    trust_remote_code (`bool`, *optional*, defaults to `False`):
-        Whether to trust remote code when using other models than SuperPoint as keypoint detector.

     Examples:
         ```python
@@ -86,10 +84,6 @@ class LightGlueConfig(PreTrainedConfig):
     hidden_act: str = "gelu"
     attention_dropout: float | int = 0.0
     attention_bias: bool = True
-    # LightGlue can be used with other models than SuperPoint as keypoint detector
-    # We provide the trust_remote_code argument to allow the use of other models
-    # that are not registered in the CONFIG_MAPPING dictionary (for example DISK)
-    trust_remote_code: bool = False

     def __post_init__(self, **kwargs):
         if self.num_key_value_heads is None:
@@ -99,14 +93,9 @@ def __post_init__(self, **kwargs):
         # See https://github.com/huggingface/transformers/pull/31718#discussion_r2109733153
         if isinstance(self.keypoint_detector_config, dict):
             self.keypoint_detector_config["model_type"] = self.keypoint_detector_config.get("model_type", "superpoint")
-            if self.keypoint_detector_config["model_type"] not in CONFIG_MAPPING:
-                self.keypoint_detector_config = AutoConfig.from_pretrained(
-                    self.keypoint_detector_config["_name_or_path"], trust_remote_code=self.trust_remote_code
-                )
-            else:
-                self.keypoint_detector_config = CONFIG_MAPPING[self.keypoint_detector_config["model_type"]](
-                    **self.keypoint_detector_config, attn_implementation="eager"
-                )
+            self.keypoint_detector_config = CONFIG_MAPPING[self.keypoint_detector_config["model_type"]](
+                **self.keypoint_detector_config, attn_implementation="eager"
+            )
         elif self.keypoint_detector_config is None:
             self.keypoint_detector_config = CONFIG_MAPPING["superpoint"](attn_implementation="eager")

@@ -520,9 +509,7 @@ class LightGlueForKeypointMatching(LightGluePreTrainedModel):

     def __init__(self, config: LightGlueConfig):
         super().__init__(config)
-        self.keypoint_detector = AutoModelForKeypointDetection.from_config(
-            config.keypoint_detector_config, trust_remote_code=config.trust_remote_code
-        )
+        self.keypoint_detector = AutoModelForKeypointDetection.from_config(config.keypoint_detector_config)

         self.keypoint_detector_descriptor_dim = config.keypoint_detector_config.descriptor_decoder_dim
         self.descriptor_dim = config.descriptor_dim
diff --git a/utils/mlinter/rules.toml b/utils/mlinter/rules.toml
index a5b8439e0be0..4294f53f3e14 100644
--- a/utils/mlinter/rules.toml
+++ b/utils/mlinter/rules.toml
@@ -241,3 +241,24 @@ class FooModel(FooPreTrainedModel):
         self.layers = nn.ModuleList(...)
         self.post_init()
 '''
+
+[rules.TRF014]
+description = "`trust_remote_code` should never be used in native model integrations."
+default_enabled = true
+allowlist_models = []
+
+[rules.TRF014.explanation]
+what_it_does = "Checks whether `trust_remote_code` is passed or used in code (e.g. as kwarg) within native model integration files."
+why_bad = "`trust_remote_code` allows arbitrary loading, including binaries, which should only be a power feature for users, not a standard use-case. Native integrations must not depend on it, as remote code cannot be reviewed or maintained within transformers."
+bad_example = '''
+class FooModel(FooPreTrainedModel):
+    def __init__(self, config):
+        super().__init__(config)
+        self.model = AutoModel.from_pretrained(..., trust_remote_code=True)
+'''
+good_example = '''
+class FooModel(FooPreTrainedModel):
+    def __init__(self, config):
+        super().__init__(config)
+        self.model = AutoModel.from_pretrained(...)
+'''
diff --git a/utils/mlinter/trf014.py b/utils/mlinter/trf014.py
new file mode 100644
index 000000000000..01e85ed4507b
--- /dev/null
+++ b/utils/mlinter/trf014.py
@@ -0,0 +1,77 @@
+# Copyright 2026 The HuggingFace Team. All rights reserved.
+#
+# Licensed under the Apache License, Version 2.0 (the "License");
+# you may not use this file except in compliance with the License.
+# You may obtain a copy of the License at
+#
+#     http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing, software
+# distributed under the License is distributed on an "AS IS" BASIS,
+# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+# See the License for the specific language governing permissions and
+# limitations under the License.
+
+"""TRF014: `trust_remote_code` should never be used in native model integrations."""
+
+import ast
+from pathlib import Path
+
+from ._helpers import Violation
+
+
+RULE_ID = ""  # Set by discovery
+
+
+class TrustRemoteCodeVisitor(ast.NodeVisitor):
+    def __init__(self, file_path: Path):
+        self.file_path = file_path
+        self.violations: list[Violation] = []
+
+    def _add(self, node: ast.AST, message: str) -> None:
+        self.violations.append(
+            Violation(
+                file_path=self.file_path,
+                line_number=node.lineno,
+                message=f"{RULE_ID}: {message}",
+            )
+        )
+
+    def visit_Call(self, node: ast.Call) -> None:
+        """
+        Three cases covered by this
+            1. `foo(..., trust_remote_code=...)`
+            2. `foo(**{..., "trust_remote_code": ...})`
+            3. `foo(**dict(trust_remote_code=...))`
+
+        Not covered:
+               `kwargs = {"trust_remote_code": True}; foo(**kwargs)`
+        """
+        for keyword in node.keywords:
+            if keyword.arg == "trust_remote_code":
+                self._add(node, "`trust_remote_code` must not be passed as a keyword argument.")
+
+            elif keyword.arg is None:
+                value = keyword.value
+
+                if isinstance(value, ast.Dict):
+                    for key in value.keys:
+                        if isinstance(key, ast.Constant) and key.value == "trust_remote_code":
+                            self._add(node, "`trust_remote_code` must not be passed through `**kwargs`.")
+
+                elif isinstance(value, ast.Call):
+                    if isinstance(value.func, ast.Name) and value.func.id == "dict":
+                        for kw in value.keywords:
+                            if kw.arg == "trust_remote_code":
+                                self._add(
+                                    node,
+                                    "`trust_remote_code` must not be passed through `**kwargs` (dict constructor).",
+                                )
+
+        self.generic_visit(node)
+
+
+def check(tree: ast.Module, file_path: Path, source_lines: list[str]) -> list[Violation]:
+    visitor = TrustRemoteCodeVisitor(file_path)
+    visitor.visit(tree)
+    return visitor.violations
PATCH

echo "Patch applied successfully."
