#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

TARGET="src/transformers/models/nemotron_h/configuration_nemotron_h.py"

# Idempotency: check if already fixed (n_groups docstring present in the right section)
if grep -q '    n_groups (`int`, \*optional\*, default to 8):' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/nemotron_h/configuration_nemotron_h.py b/src/transformers/models/nemotron_h/configuration_nemotron_h.py
index 99c7a40457bc..f2ab3ed25ebd 100644
--- a/src/transformers/models/nemotron_h/configuration_nemotron_h.py
+++ b/src/transformers/models/nemotron_h/configuration_nemotron_h.py
@@ -39,14 +39,14 @@ class NemotronHConfig(PreTrainedConfig):
         Number of groups for expert routing.
     mamba_hidden_act (`str`, *optional*, defaults to `"silu"`):
         The non-linear activation function in the Mamba layers.
-    mamba_dt_min (`float`, *optional*, defaults to 0.001):
-        Minimum value for the time step in Mamba.
-    mamba_dt_max (`float`, *optional*, defaults to 0.1):
-        Maximum value for the time step in Mamba.
-    mamba_dt_limit (`tuple`, *optional*, defaults to `(0.0, inf)`):
-        Limits for the time step in Mamba.
-    mamba_dt_init_floor (`float`, *optional*, defaults to 0.0001):
-        Floor value for time step initialization in Mamba.
+    n_groups (`int`, *optional*, default to 8):
+        Number of mamba groups.
+    expand (`int`, *optional*, default to 2):
+        Expand size for the mamba layers.
+    use_conv_bias (`bool`, *optional*, defaults to `True`):
+        Whetehr to use bias for mamba conv layers.
+    chunk_size (`int`, *optional*, default to 128):
+        CHunk size for mamba layers.
     mamba_ssm_cache_dtype (`str`, *optional*, defaults to `"float32"`):
         Data type for Mamba SSM cache states.
     moe_shared_expert_intermediate_size (`int`, *optional*, defaults to 7688):

PATCH

echo "Patch applied successfully."
