#!/usr/bin/env bash
set -euo pipefail

cd /workspace/huggingface__transformers || cd /workspace

# Idempotency: check if already fixed (no "# Copied from" between @torch.jit.script and def)
DEBERTA_FILE="src/transformers/models/deberta_v2/modeling_deberta_v2.py"
SEW_D_FILE="src/transformers/models/sew_d/modeling_sew_d.py"

if ! grep -A1 '@torch.jit.script' "$DEBERTA_FILE" | grep -q '# Copied from'; then
    echo "Already fixed."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/deberta_v2/modeling_deberta_v2.py b/src/transformers/models/deberta_v2/modeling_deberta_v2.py
index f6b25925797d..b30cbd6342dc 100644
--- a/src/transformers/models/deberta_v2/modeling_deberta_v2.py
+++ b/src/transformers/models/deberta_v2/modeling_deberta_v2.py
@@ -102,19 +102,16 @@ def build_relative_position(query_layer, key_layer, bucket_size: int = -1, max_p


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.c2p_dynamic_expand
 def c2p_dynamic_expand(c2p_pos, query_layer, relative_pos):
     return c2p_pos.expand([query_layer.size(0), query_layer.size(1), query_layer.size(2), relative_pos.size(-1)])


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.p2c_dynamic_expand
 def p2c_dynamic_expand(c2p_pos, query_layer, key_layer):
     return c2p_pos.expand([query_layer.size(0), query_layer.size(1), key_layer.size(-2), key_layer.size(-2)])


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.pos_dynamic_expand
 def pos_dynamic_expand(pos_index, p2c_att, key_layer):
     return pos_index.expand(p2c_att.size()[:2] + (pos_index.size(-2), key_layer.size(-2)))

diff --git a/src/transformers/models/sew_d/modeling_sew_d.py b/src/transformers/models/sew_d/modeling_sew_d.py
index bc573ee73c96..15323596c71a 100644
--- a/src/transformers/models/sew_d/modeling_sew_d.py
+++ b/src/transformers/models/sew_d/modeling_sew_d.py
@@ -202,19 +202,16 @@ def build_relative_position(query_size, key_size, bucket_size=-1, max_position=-


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.c2p_dynamic_expand
 def c2p_dynamic_expand(c2p_pos, query_layer, relative_pos):
     return c2p_pos.expand([query_layer.size(0), query_layer.size(1), query_layer.size(2), relative_pos.size(-1)])


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.p2c_dynamic_expand
 def p2c_dynamic_expand(c2p_pos, query_layer, key_layer):
     return c2p_pos.expand([query_layer.size(0), query_layer.size(1), key_layer.size(-2), key_layer.size(-2)])


 @torch.jit.script
-# Copied from transformers.models.deberta.modeling_deberta.pos_dynamic_expand
 def pos_dynamic_expand(pos_index, p2c_att, key_layer):
     return pos_index.expand(p2c_att.size()[:2] + (pos_index.size(-2), key_layer.size(-2)))

PATCH

echo "Patch applied successfully."
