#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

TARGET="src/transformers/modeling_utils.py"

# Check if already applied: supports_tp_plan should use truthiness, not 'is not None'
if python3 -c "
import ast, sys
with open('$TARGET') as f: src = f.read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PreTrainedModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'supports_tp_plan':
                func_src = '\n'.join(src.splitlines()[item.lineno-1:item.end_lineno])
                if '_tp_plan is not None' not in func_src:
                    sys.exit(0)  # already fixed
sys.exit(1)
" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Try git apply first
cat > /tmp/patch.diff << 'PATCH'
diff --git a/src/transformers/modeling_utils.py b/src/transformers/modeling_utils.py
index e31af9847811..e38829de7deb 100644
--- a/src/transformers/modeling_utils.py
+++ b/src/transformers/modeling_utils.py
@@ -26,7 +26,6 @@
 from collections.abc import Callable, Iterator
 from contextlib import contextmanager
 from dataclasses import dataclass, field
-from enum import Enum
 from functools import partial, wraps
 from itertools import cycle
 from threading import Thread
@@ -832,11 +831,6 @@ def _get_dtype(
     return config, main_dtype


-class PipelineParallel(Enum):
-    inputs = 0
-    outputs = 1
-
-
 class ModuleUtilsMixin:
     """
     A few utilities for `torch.nn.Modules`, to be used as a mixin.
@@ -1155,7 +1149,7 @@ class PreTrainedModel(nn.Module, EmbeddingAccessMixin, ModuleUtilsMixin, PushToH
     # A pipeline parallel plan specifying the layers which may not be present on all ranks when PP is enabled. For top-level
     # models, this attribute is currently defined in respective model code. For base models, it comes from
     # `config.base_model_pp_plan` during `post_init`.
-    _pp_plan: dict[str, PipelineParallel] | None = None
+    _pp_plan: dict[str, tuple[str, str]] = None

     # Advanced functionalities support
     supports_gradient_checkpointing: bool = False
@@ -1380,7 +1374,13 @@ def tp_plan(self, plan: dict[str, str] | None):
         self._tp_plan = plan

     @pp_plan.setter
-    def pp_plan(self, plan: dict[str, tuple[str, str]]):
+    def pp_plan(self, plan: dict[str, tuple[str, str]] | None):
+        if plan is None:
+            self._pp_plan = {}
+            return
+        if not isinstance(plan, dict):
+            raise ValueError("Can only set a dictionary as `pp_plan`")
+
         self._pp_plan = plan

     def dequantize(self, dtype=None):
@@ -4385,12 +4385,14 @@ def supports_tp_plan(self):
         """
         Returns whether the model has a tensor parallelism plan.
         """
-        if self._tp_plan is not None:
+        # Check if model has a TP plan
+        if self._tp_plan:
             return True
         # Check if base model has a TP plan
-        if getattr(self.base_model, "_tp_plan", None) is not None:
+        if self.base_model._tp_plan:
             return True
-        if self.config.base_model_tp_plan is not None:
+        # Check if config has TP plan
+        if self.config.base_model_tp_plan:
             return True
         return False

@@ -4404,10 +4406,14 @@ def tp_size(self):

     @property
     def supports_pp_plan(self):
-        if self._pp_plan is not None:
+        # Check if model has a PP plan
+        if self._pp_plan:
             return True
         # Check if base model has PP plan
-        if getattr(self.base_model, "_pp_plan", None) is not None:
+        if self.base_model._pp_plan:
+            return True
+        # Check if config has PP plan
+        if self.config.base_model_pp_plan:
             return True
         return False

PATCH

if git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff; then
    echo "Patch applied via git apply."
    exit 0
fi

echo "git apply failed, applying changes via python..."

python3 << 'PYEOF'
import re

target = "src/transformers/modeling_utils.py"
with open(target) as f:
    content = f.read()

# 1. Remove 'from enum import Enum' line
content = content.replace("from enum import Enum\n", "")

# 2. Remove PipelineParallel class
content = re.sub(
    r'\nclass PipelineParallel\(Enum\):\n    inputs = 0\n    outputs = 1\n\n\n',
    '\n',
    content
)

# 3. Change _pp_plan type annotation
content = content.replace(
    "_pp_plan: dict[str, PipelineParallel] | None = None",
    "_pp_plan: dict[str, tuple[str, str]] = None"
)

# 4. Fix pp_plan setter - add None handling and validation
content = content.replace(
    "    def pp_plan(self, plan: dict[str, tuple[str, str]]):\n        self._pp_plan = plan",
    '    def pp_plan(self, plan: dict[str, tuple[str, str]] | None):\n'
    '        if plan is None:\n'
    '            self._pp_plan = {}\n'
    '            return\n'
    '        if not isinstance(plan, dict):\n'
    '            raise ValueError("Can only set a dictionary as `pp_plan`")\n'
    '\n'
    '        self._pp_plan = plan'
)

# 5. Fix supports_tp_plan: change 'is not None' to truthiness
content = content.replace(
    "        if self._tp_plan is not None:\n            return True\n        # Check if base model has a TP plan\n        if getattr(self.base_model, \"_tp_plan\", None) is not None:\n            return True\n        if self.config.base_model_tp_plan is not None:",
    "        # Check if model has a TP plan\n        if self._tp_plan:\n            return True\n        # Check if base model has a TP plan\n        if self.base_model._tp_plan:\n            return True\n        # Check if config has TP plan\n        if self.config.base_model_tp_plan:"
)

# 6. Fix supports_pp_plan: change 'is not None' to truthiness and add config check
content = content.replace(
    "        if self._pp_plan is not None:\n            return True\n        # Check if base model has PP plan\n        if getattr(self.base_model, \"_pp_plan\", None) is not None:\n            return True\n        return False",
    "        # Check if model has a PP plan\n        if self._pp_plan:\n            return True\n        # Check if base model has PP plan\n        if self.base_model._pp_plan:\n            return True\n        # Check if config has PP plan\n        if self.config.base_model_pp_plan:\n            return True\n        return False"
)

with open(target, 'w') as f:
    f.write(content)
print("Python fallback applied successfully.")
PYEOF
