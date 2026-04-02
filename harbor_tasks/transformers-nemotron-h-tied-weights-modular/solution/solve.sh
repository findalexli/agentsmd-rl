#!/usr/bin/env bash
set -euo pipefail

MODELING="src/transformers/models/nemotron_h/modeling_nemotron_h.py"
MODULAR="src/transformers/models/nemotron_h/modular_nemotron_h.py"

# Idempotency: exit early if _tied_weights_keys is already absent from base class
if python3 -c "
import ast, sys
with open('$MODELING') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHPreTrainedModel':
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '_tied_weights_keys':
                        sys.exit(1)  # still present, patch needed
sys.exit(0)  # already removed
" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/nemotron_h/modeling_nemotron_h.py b/src/transformers/models/nemotron_h/modeling_nemotron_h.py
index e2f7d1063290..e9ca8d462f43 100644
--- a/src/transformers/models/nemotron_h/modeling_nemotron_h.py
+++ b/src/transformers/models/nemotron_h/modeling_nemotron_h.py
@@ -1083,7 +1083,6 @@ class NemotronHPreTrainedModel(PreTrainedModel):
     _keep_in_fp32_modules_strict = [
         "e_score_correction_bias",
     ]
-    _tied_weights_keys = {}
     _keys_to_ignore_on_load_unexpected = [r"mtp.*"]

     @torch.no_grad()
@@ -1247,7 +1246,7 @@ def _update_mamba_mask(self, attention_mask, past_key_values):
 class NemotronHForCausalLM(NemotronHPreTrainedModel, GenerationMixin):
     _tied_weights_keys = {}

-    def __init__(self, config):
+    def __init__(self, config: NemotronHConfig):
         super().__init__(config)
         self.model = NemotronHModel(config)
         self.vocab_size = config.vocab_size
diff --git a/src/transformers/models/nemotron_h/modular_nemotron_h.py b/src/transformers/models/nemotron_h/modular_nemotron_h.py
index ab9f24718c00..ea186fbc5647 100644
--- a/src/transformers/models/nemotron_h/modular_nemotron_h.py
+++ b/src/transformers/models/nemotron_h/modular_nemotron_h.py
@@ -354,7 +354,6 @@ class NemotronHPreTrainedModel(PreTrainedModel):
     _keep_in_fp32_modules_strict = [
         "e_score_correction_bias",
     ]
-    _tied_weights_keys = {}
     _keys_to_ignore_on_load_unexpected = [r"mtp.*"]

     @torch.no_grad()
@@ -517,10 +516,6 @@ def _update_mamba_mask(self, attention_mask, past_key_values):
 class NemotronHForCausalLM(ZambaForCausalLM):
     _tied_weights_keys = {}

-    def __init__(self, config):
-        super().__init__(config)
-        del self._tied_weights_keys
-
     @can_return_tuple
     @auto_docstring
     def forward(

PATCH

echo "Patch applied successfully."
