#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency check: if mamba_expand is already computed from heads, skip
if grep -q 'mamba_expand = (mamba_num_heads \* mamba_head_dim) / hidden_size' \
    src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py b/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py
index 5c3891d3cb..c1962737a7 100644
--- a/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py
+++ b/src/prime_rl/trainer/models/nemotron_h/configuration_nemotron_h.py
@@ -170,10 +170,13 @@ def __init__(
         self.mamba_proj_bias = mamba_proj_bias
         self.chunk_size = mamba_chunk_size

-        # Zamba2MambaMixer compat aliases (read by parent __init__ before NemotronHMamba2Mixer overrides)
+        # Zamba2MambaMixer compat aliases (read by parent __init__ before NemotronHMamba2Mixer overrides).
+        # mamba_expand must give the correct intermediate_size = mamba_num_heads * mamba_head_dim
+        # when Zamba2 computes int(mamba_expand * hidden_size); the config's raw "expand" field
+        # does not satisfy this for all model sizes (e.g. Nemotron-3-Nano-30B).
         self.mamba_d_state = ssm_state_size
         self.mamba_d_conv = mamba_d_conv
-        self.mamba_expand = mamba_expand
+        self.mamba_expand = (mamba_num_heads * mamba_head_dim) / hidden_size
         self.mamba_ngroups = mamba_n_groups
         self.mamba_headdim = mamba_head_dim
         self.n_mamba_heads = mamba_num_heads
diff --git a/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py b/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py
index b3af1b3d89..fef4203e9b 100644
--- a/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py
+++ b/src/prime_rl/trainer/models/nemotron_h/modeling_nemotron_h.py
@@ -81,12 +81,44 @@ def _patched_forward(self, hidden_states, cache_params=None, attention_mask=None
     logger.info("Patched NemotronHMamba2Mixer to use mamba_ssm Triton SSD kernels")


+def _ensure_zamba2_compat(config: NemotronHConfig):
+    """Add Zamba2-compatible attribute aliases to NemotronHConfig.
+
+    The HF modular NemotronHMamba2Mixer inherits from Zamba2MambaMixer, whose
+    __init__ reads Zamba2-style attribute names before the NemotronH child
+    overrides them. We set the missing aliases so the parent __init__ doesn't
+    crash.
+
+    Critically, ``mamba_expand`` must give ``mamba_num_heads * mamba_head_dim``
+    when multiplied by ``hidden_size``; the config's ``expand`` field does not
+    satisfy this for all model sizes (e.g. Nemotron-3-Nano-30B).
+    """
+    correct_intermediate = config.mamba_num_heads * config.mamba_head_dim
+    correct_expand = correct_intermediate / config.hidden_size
+
+    aliases = {
+        "mamba_d_state": config.ssm_state_size,
+        "mamba_d_conv": config.conv_kernel,
+        "mamba_ngroups": config.n_groups,
+        "mamba_headdim": config.mamba_head_dim,
+        "n_mamba_heads": config.mamba_num_heads,
+        "add_bias_linear": getattr(config, "use_bias", False),
+        "use_mem_eff_path": True,
+    }
+    for attr, value in aliases.items():
+        if not hasattr(config, attr):
+            setattr(config, attr, value)
+
+    config.mamba_expand = correct_expand
+
+
 class NemotronHMambaLayer(GradientCheckpointingLayer):
     """Mamba-2 SSM layer: norm -> NemotronHMamba2Mixer -> residual."""

     def __init__(self, config: NemotronHConfig, layer_idx: int):
         super().__init__()
         _patch_mamba2_use_triton_ssd()
+        _ensure_zamba2_compat(config)
         self.norm = RMSNorm(RMSNormConfig(hidden_size=config.hidden_size, eps=config.layer_norm_epsilon))
         self.mamba = NemotronHMamba2Mixer(config, layer_idx=layer_idx)
         self.mlp = None  # No MoE in this layer type

PATCH

echo "Patch applied successfully."
