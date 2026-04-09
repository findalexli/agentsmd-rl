#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'get_gpt_decoder_block_spec' slime_plugins/megatron_bridge/glm4v_moe.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime_plugins/megatron_bridge/glm4v_moe.py b/slime_plugins/megatron_bridge/glm4v_moe.py
index 3fd758314..c213096a8 100644
--- a/slime_plugins/megatron_bridge/glm4v_moe.py
+++ b/slime_plugins/megatron_bridge/glm4v_moe.py
@@ -25,10 +25,9 @@
 from megatron.bridge.utils.common_utils import hook_hf_module_setattr_for_tp_grad_sync
 from megatron.core import parallel_state, tensor_parallel
 from megatron.core.models.gpt import GPTModel as MCoreGPTModel
-from megatron.core.models.gpt.gpt_layer_specs import get_gpt_layer_with_transformer_engine_spec
+from megatron.core.models.gpt.gpt_layer_specs import get_gpt_decoder_block_spec
 from megatron.core.packed_seq_params import PackedSeqParams
 from megatron.core.transformer.module import MegatronModule
-from megatron.core.transformer.spec_utils import ModuleSpec

 logger = logging.getLogger(__name__)

@@ -117,7 +116,7 @@ class Glm4vMoeVLModel(MegatronModule):
     def __init__(
         self,
         language_transformer_config,
-        language_transformer_layer_spec: ModuleSpec,
+        language_transformer_layer_spec,
         hf_vision_config,
         parallel_output: bool = True,
         pre_process: bool = True,
@@ -427,11 +426,11 @@ def provide(self, pre_process=None, post_process=None, vp_stage=None):
         if post_process is None:
             post_process = parallel_state.is_pipeline_last_stage(ignore_virtual=False, vp_stage=vp_stage)

-        # Build transformer layer spec for MoE
-        transformer_layer_spec = get_gpt_layer_with_transformer_engine_spec(
-            num_experts=self.num_moe_experts,
-            moe_grouped_gemm=self.moe_grouped_gemm,
-            qk_layernorm=self.qk_layernorm,
+        # Build per-layer specs respecting moe_layer_freq (layer 0 = dense, rest = MoE)
+        transformer_layer_spec = get_gpt_decoder_block_spec(
+            config=self,
+            use_transformer_engine=True,
+            vp_stage=vp_stage,
         )

         model = Glm4vMoeVLModel(
@@ -478,8 +477,8 @@ def provider_bridge(self, hf_pretrained):
         # Determine MoE layer frequency
         first_k_dense = getattr(text_config, "first_k_dense_replace", 1)
         num_layers = text_config.num_hidden_layers
-        # Build moe_layer_freq string: first_k_dense dense layers + rest MoE
-        moe_layer_freq_str = f"[0]*{first_k_dense}+[1]*{num_layers - first_k_dense}"
+        # Build moe_layer_freq list: first_k_dense dense layers + rest MoE
+        moe_layer_freq_list = [0] * first_k_dense + [1] * (num_layers - first_k_dense)

         # Shared expert intermediate size
         n_shared = getattr(text_config, "n_shared_experts", 1)
@@ -511,7 +510,7 @@ def provider_bridge(self, hf_pretrained):
             moe_router_topk=getattr(text_config, "num_experts_per_tok", 8),
             moe_ffn_hidden_size=moe_ffn,
             moe_shared_expert_intermediate_size=shared_expert_intermediate,
-            moe_layer_freq=moe_layer_freq_str,
+            moe_layer_freq=moe_layer_freq_list,
             moe_grouped_gemm=True,
             moe_router_load_balancing_type="seq_aux_loss",
             moe_aux_loss_coeff=0,

PATCH

echo "Patch applied successfully."
