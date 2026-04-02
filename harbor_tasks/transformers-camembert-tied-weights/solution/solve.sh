#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

MODELING="src/transformers/models/camembert/modeling_camembert.py"
MODULAR="src/transformers/models/camembert/modular_camembert.py"

# Check if patch is already applied by looking for the BUGGY line.
# Note: CamembertForMaskedLM already has the correct "roberta" path,
# so we can't grep for the fixed string — we must check the buggy one is gone.
if ! grep -q '"lm_head.decoder.weight": "camembert.embeddings.word_embeddings.weight"' "$MODELING"; then
    echo "Patch already applied."
    exit 0
fi

# Try git apply first
APPLIED=false
git apply - <<'PATCH' && APPLIED=true || true
diff --git a/src/transformers/models/camembert/modeling_camembert.py b/src/transformers/models/camembert/modeling_camembert.py
index 9097ac9bf6e1..0c8a76fc7c6c 100644
--- a/src/transformers/models/camembert/modeling_camembert.py
+++ b/src/transformers/models/camembert/modeling_camembert.py
@@ -1154,7 +1154,7 @@ def forward(
 )
 class CamembertForCausalLM(CamembertPreTrainedModel, GenerationMixin):
     _tied_weights_keys = {
-        "lm_head.decoder.weight": "camembert.embeddings.word_embeddings.weight",
+        "lm_head.decoder.weight": "roberta.embeddings.word_embeddings.weight",
         "lm_head.decoder.bias": "lm_head.bias",
     }

diff --git a/src/transformers/models/camembert/modular_camembert.py b/src/transformers/models/camembert/modular_camembert.py
index 2f5bf2825bf5..f3f06a2c70f6 100644
--- a/src/transformers/models/camembert/modular_camembert.py
+++ b/src/transformers/models/camembert/modular_camembert.py
@@ -427,6 +427,11 @@ def forward(


 class CamembertForCausalLM(RobertaForCausalLM):
+    _tied_weights_keys = {
+        "lm_head.decoder.weight": "roberta.embeddings.word_embeddings.weight",
+        "lm_head.decoder.bias": "lm_head.bias",
+    }
+
     def __init__(self, config):
         super().__init__(config)
         del self.camembert

PATCH

if [ "$APPLIED" = true ]; then
    echo "Patch applied via git apply."
    exit 0
fi

echo "git apply failed, falling back to sed/python..."

# Fallback: fix modeling_camembert.py with sed
sed -i 's/"lm_head.decoder.weight": "camembert.embeddings.word_embeddings.weight"/"lm_head.decoder.weight": "roberta.embeddings.word_embeddings.weight"/' "$MODELING"

# Fallback: add _tied_weights_keys to modular_camembert.py CamembertForCausalLM class
python3 << 'PYEOF'
import re

target = "src/transformers/models/camembert/modular_camembert.py"
with open(target) as f:
    content = f.read()

# Check if _tied_weights_keys already exists in CamembertForCausalLM
if '"lm_head.decoder.weight": "roberta.embeddings.word_embeddings.weight"' in content:
    print("modular file already patched")
else:
    # Insert _tied_weights_keys after the class definition line
    pattern = r'(class CamembertForCausalLM\(RobertaForCausalLM\):\n)'
    replacement = r'''\1    _tied_weights_keys = {
        "lm_head.decoder.weight": "roberta.embeddings.word_embeddings.weight",
        "lm_head.decoder.bias": "lm_head.bias",
    }

'''
    new_content = re.sub(pattern, replacement, content)
    with open(target, 'w') as f:
        f.write(new_content)
    print("modular file patched via python fallback")
PYEOF

echo "Fallback patch applied."
