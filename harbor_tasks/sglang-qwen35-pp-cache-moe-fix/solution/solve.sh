#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency check: if the fix is already applied, skip
if grep -q 'mamba_layer_ids: List\[int\]' python/sglang/srt/mem_cache/memory_pool.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/disaggregation/decode.py b/python/sglang/srt/disaggregation/decode.py
index ce7ae1557447..f5df357eb25a 100644
--- a/python/sglang/srt/disaggregation/decode.py
+++ b/python/sglang/srt/disaggregation/decode.py
@@ -174,11 +174,13 @@ def __init__(
         device: str,
         enable_memory_saver: bool,
         cache_params: "Mamba2CacheParams",
+        mamba_layer_ids: List[int],
         speculative_num_draft_tokens: int,
         enable_mamba_extra_buffer: bool,
         pre_alloc_size: int,
         enable_overlap_schedule: bool,
         mamba_size: int = None,
+        start_layer: int = None,
     ):
         DecodeReqToTokenPool.__init__(
             self,
@@ -195,13 +197,13 @@ def __init__(
         effective_mamba_size = (
             mamba_size if mamba_size is not None else size
         ) + pre_alloc_size
-        # TODO: Support PP
-        self.start_layer = 0
+        self.start_layer = start_layer if start_layer is not None else 0
         self.layer_transfer_counter = None
         self._init_mamba_pool(
             size=effective_mamba_size,
             mamba_spec_state_size=size + pre_alloc_size,
             cache_params=cache_params,
+            mamba_layer_ids=mamba_layer_ids,
             device=device,
             enable_mamba_extra_buffer=self.enable_mamba_extra_buffer,
             speculative_num_draft_tokens=speculative_num_draft_tokens,
diff --git a/python/sglang/srt/mem_cache/memory_pool.py b/python/sglang/srt/mem_cache/memory_pool.py
index 881f3cad77a2..df5d54223c22 100644
--- a/python/sglang/srt/mem_cache/memory_pool.py
+++ b/python/sglang/srt/mem_cache/memory_pool.py
@@ -220,6 +220,7 @@ def __init__(
         size: int,
         spec_state_size: int,
         cache_params: BaseLinearStateParams,
+        mamba_layer_ids: List[int],
         device: str,
         enable_memory_saver: bool = False,
         speculative_num_draft_tokens: Optional[int] = None,
@@ -231,7 +232,7 @@ def __init__(
         self.memory_saver_adapter = TorchMemorySaverAdapter.create(
             enable=enable_memory_saver
         )
-        num_mamba_layers = len(cache_params.layers)
+        num_mamba_layers = len(mamba_layer_ids)

         self.size = size
         self.device = device
@@ -454,9 +455,11 @@ def __init__(
         device: str,
         enable_memory_saver: bool,
         cache_params: BaseLinearStateParams,
+        mamba_layer_ids: List[int],
         enable_mamba_extra_buffer: bool,
         speculative_num_draft_tokens: int = None,
         enable_overlap_schedule: bool = True,
+        start_layer: Optional[int] = None,
     ):
         super().__init__(
             size=size,
@@ -468,13 +471,13 @@ def __init__(
         self.mamba_ping_pong_track_buffer_size = 2 if enable_overlap_schedule else 1
         self.enable_mamba_extra_buffer = enable_mamba_extra_buffer
         self.enable_memory_saver = enable_memory_saver
-        # TODO: Support PP
-        self.start_layer = 0
+        self.start_layer = start_layer if start_layer is not None else 0
         self.layer_transfer_counter = None
         self._init_mamba_pool(
             size=mamba_size,
             mamba_spec_state_size=mamba_spec_state_size,
             cache_params=cache_params,
+            mamba_layer_ids=mamba_layer_ids,
             device=device,
             enable_mamba_extra_buffer=enable_mamba_extra_buffer,
             speculative_num_draft_tokens=speculative_num_draft_tokens,
@@ -485,6 +488,7 @@ def _init_mamba_pool(
         size: int,
         mamba_spec_state_size: int,
         cache_params: BaseLinearStateParams,
+        mamba_layer_ids: List[int],
         device: str,
         enable_mamba_extra_buffer: bool,
         speculative_num_draft_tokens: int = None,
@@ -493,11 +497,12 @@ def _init_mamba_pool(
             size=size,
             spec_state_size=mamba_spec_state_size,
             cache_params=cache_params,
+            mamba_layer_ids=mamba_layer_ids,
             device=device,
             enable_memory_saver=self.enable_memory_saver,
             speculative_num_draft_tokens=speculative_num_draft_tokens,
         )
-        self.mamba_map = {layer_id: i for i, layer_id in enumerate(cache_params.layers)}
+        self.mamba_map = {layer_id: i for i, layer_id in enumerate(mamba_layer_ids)}

         self.device = device
         self.req_index_to_mamba_index_mapping: torch.Tensor = torch.zeros(
@@ -1235,13 +1240,14 @@ def __init__(
         use_mla: bool = False,
         kv_lora_rank: int = None,
         qk_rope_head_dim: int = None,
+        start_layer: Optional[int] = None,
     ):
         self.size = size
         self.dtype = dtype
         self.device = device
         self.full_layer_nums = len(full_attention_layer_ids)
         self.page_size = page_size
-        self.start_layer = 0  # TODO: Support PP
+        self.start_layer = start_layer if start_layer is not None else 0
         self.layer_transfer_counter = None
         self.head_num = head_num
         self.head_dim = head_dim
diff --git a/python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py b/python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py
index a021c6561d03..c65e4a440c0d 100644
--- a/python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py
+++ b/python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py
@@ -401,11 +401,19 @@ def _init_pools(self: ModelRunner):
                         device=self.device,
                         enable_memory_saver=self.server_args.enable_memory_saver,
                         cache_params=config.mamba2_cache_params,
+                        mamba_layer_ids=(
+                            [
+                                i
+                                for i in config.mamba2_cache_params.layers
+                                if self.start_layer <= i < self.end_layer
+                            ]
+                        ),
                         speculative_num_draft_tokens=self.server_args.speculative_num_draft_tokens,
                         enable_mamba_extra_buffer=self.server_args.enable_mamba_extra_buffer(),
                         pre_alloc_size=pre_alloc_size,
                         enable_overlap_schedule=not self.server_args.disable_overlap_schedule,
                         mamba_size=self.server_args.max_mamba_cache_size,
+                        start_layer=self.start_layer,
                     )
                 else:
                     self.req_to_token_pool = DecodeReqToTokenPool(
@@ -426,9 +434,17 @@ def _init_pools(self: ModelRunner):
                     device=self.device,
                     enable_memory_saver=self.server_args.enable_memory_saver,
                     cache_params=config.mamba2_cache_params,
+                    mamba_layer_ids=(
+                        [
+                            i
+                            for i in config.mamba2_cache_params.layers
+                            if self.start_layer <= i < self.end_layer
+                        ]
+                    ),
                     enable_mamba_extra_buffer=self.server_args.enable_mamba_extra_buffer(),
                     speculative_num_draft_tokens=self.server_args.speculative_num_draft_tokens,
                     enable_overlap_schedule=not self.server_args.disable_overlap_schedule,
+                    start_layer=self.start_layer,
                 )
             else:
                 self.req_to_token_pool = ReqToTokenPool(
@@ -610,6 +626,7 @@ def _init_pools(self: ModelRunner):
                     mamba_pool=self.req_to_token_pool.mamba_pool,
                     enable_memory_saver=self.server_args.enable_memory_saver,
                     use_mla=self.use_mla_backend,
+                    start_layer=self.start_layer,
                     **extra_args,
                 )
             else:
diff --git a/python/sglang/srt/models/qwen3_5.py b/python/sglang/srt/models/qwen3_5.py
index 45b55fa3bd09..bbd38d9386cf 100644
--- a/python/sglang/srt/models/qwen3_5.py
+++ b/python/sglang/srt/models/qwen3_5.py
@@ -67,7 +67,7 @@
 from sglang.srt.layers.radix_attention import RadixAttention
 from sglang.srt.layers.radix_linear_attention import RadixLinearAttention
 from sglang.srt.layers.rotary_embedding import get_rope
-from sglang.srt.layers.utils import PPMissingLayer
+from sglang.srt.layers.utils import PPMissingLayer, get_layer_id
 from sglang.srt.layers.vocab_parallel_embedding import VocabParallelEmbedding
 from sglang.srt.model_executor.cuda_graph_runner import get_is_capture_mode
 from sglang.srt.model_executor.forward_batch_info import ForwardBatch, PPProxyTensors
@@ -1038,6 +1038,13 @@ def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]):
                 name = name.replace(r"model.language_model.", r"model.")
             if ".self_attn." in name:
                 name = name.replace(".self_attn", "")
+            layer_id = get_layer_id(name)
+            if (
+                layer_id is not None
+                and hasattr(self, "start_layer")
+                and (layer_id < self.start_layer or layer_id >= self.end_layer)
+            ):
+                continue

             for param_name, weight_name, shard_id in stacked_params_mapping:
                 if weight_name not in name:
@@ -1175,6 +1182,14 @@ def load_fused_expert_weights(
             if ".self_attn." in name:
                 name = name.replace(".self_attn", "")

+            layer_id = get_layer_id(name)
+            if (
+                layer_id is not None
+                and hasattr(self, "start_layer")
+                and (layer_id < self.start_layer or layer_id >= self.end_layer)
+            ):
+                continue
+
             for param_name, weight_name, shard_id in stacked_params_mapping:
                 if "experts.gate_up_proj" in name or "experts.down_proj" in name:
                     is_fused_expert = True
@@ -1355,6 +1370,13 @@ def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]):
                 name = name.replace(r"model.language_model.", r"model.")
             if ".self_attn." in name:
                 name = name.replace(".self_attn", "")
+            layer_id = get_layer_id(name)
+            if (
+                layer_id is not None
+                and hasattr(self, "start_layer")
+                and (layer_id < self.start_layer or layer_id >= self.end_layer)
+            ):
+                continue

             for param_name, weight_name, shard_id in stacked_params_mapping:
                 if weight_name not in name:
@@ -1510,6 +1532,14 @@ def load_fused_expert_weights(
             if ".self_attn." in name:
                 name = name.replace(".self_attn", "")

+            layer_id = get_layer_id(name)
+            if (
+                layer_id is not None
+                and hasattr(self, "start_layer")
+                and (layer_id < self.start_layer or layer_id >= self.end_layer)
+            ):
+                continue
+
             for param_name, weight_name, shard_id in stacked_params_mapping:
                 if name.endswith("experts.gate_up_proj") or name.endswith(
                     "experts.down_proj"
diff --git a/python/sglang/srt/models/qwen3_vl.py b/python/sglang/srt/models/qwen3_vl.py
index 1aec50d01d27..e23719e5c3e0 100644
--- a/python/sglang/srt/models/qwen3_vl.py
+++ b/python/sglang/srt/models/qwen3_vl.py
@@ -1141,6 +1141,19 @@ def separate_deepstack_embeds(self, embedding):
         input_deepstack_embeds = embedding[:, separate_index:]
         return input_embeds, input_deepstack_embeds

+    @property
+    def start_layer(self) -> int:
+        return getattr(getattr(self, "model", None), "start_layer", 0)
+
+    @property
+    def end_layer(self) -> int:
+        model = getattr(self, "model", None)
+        end_layer = getattr(model, "end_layer", None)
+        if end_layer is not None:
+            return end_layer
+        cfg = getattr(model, "config", None)
+        return int(getattr(cfg, "num_hidden_layers", 0))
+
     def pad_input_ids(self, input_ids: List[int], mm_inputs: MultimodalInputs):
         pattern = MultiModalityDataPaddingPatternMultimodalTokens()
         return pattern.pad_input_tokens(input_ids, mm_inputs)
diff --git a/test/registered/unit/mem_cache/test_mamba_unittest.py b/test/registered/unit/mem_cache/test_mamba_unittest.py
index 6955724991ec..c6219a46dee5 100644
--- a/test/registered/unit/mem_cache/test_mamba_unittest.py
+++ b/test/registered/unit/mem_cache/test_mamba_unittest.py
@@ -99,6 +99,7 @@ def test_mamba_pool(self):
             device=device,
             enable_memory_saver=False,
             cache_params=mamba2_cache_params,
+            mamba_layer_ids=mamba_layers,
             enable_mamba_extra_buffer=False,
             speculative_num_draft_tokens=3,
         )
@@ -340,6 +341,7 @@ def _setup_tree_and_allocator(self):
             device=device,
             enable_memory_saver=False,
             cache_params=mamba2_cache_params,
+            mamba_layer_ids=mamba_layers,
             enable_mamba_extra_buffer=False,
             speculative_num_draft_tokens=3,
         )

PATCH


# Also fix the test file to use CustomTestCase as required by the rubric
sed -i 's/import unittest/import unittest\n\nfrom sglang.test.test_utils import CustomTestCase/' /workspace/sglang/test/registered/unit/mem_cache/test_mamba_unittest.py
sed -i 's/class TestMamba(unittest.TestCase):/class TestMamba(CustomTestCase):/' /workspace/sglang/test/registered/unit/mem_cache/test_mamba_unittest.py
echo "Patch applied successfully."
