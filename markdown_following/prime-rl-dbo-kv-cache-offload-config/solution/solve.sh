#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'enable_dbo' src/prime_rl/configs/inference.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/configs/inference.py b/src/prime_rl/configs/inference.py
index 0347024576..747b0f999c 100644
--- a/src/prime_rl/configs/inference.py
+++ b/src/prime_rl/configs/inference.py
@@ -142,6 +142,20 @@ class MultiNodeInferenceDeploymentConfig(BaseInferenceDeploymentConfig):
     backend_port: Annotated[int, Field(description="Port for vLLM backend instances.")] = 8100


+class KVCacheOffloadConfig(BaseModel):
+    """CPU KV cache offloading for disaggregated prefill nodes.
+
+    When configured, prefill nodes use MultiConnector (NixlConnector + OffloadingConnector).
+    Decode nodes always use NixlConnector only.
+    """
+
+    model_config = ConfigDict(extra="forbid")
+
+    block_size: Annotated[int, Field(ge=1, description="Block size for the CPU offloading connector.")] = 64
+
+    cpu_bytes: Annotated[int, Field(ge=0, description="CPU bytes available for KV cache offloading.")] = 1_000_000_000
+
+
 class DisaggregatedInferenceDeploymentConfig(BaseInferenceDeploymentConfig):
     """Configures a disaggregated prefill/decode inference deployment.

@@ -187,6 +201,11 @@ class DisaggregatedInferenceDeploymentConfig(BaseInferenceDeploymentConfig):
         Field(description="Extra environment variables exported only on decode nodes."),
     ] = {}

+    kv_cache_offload: Annotated[
+        KVCacheOffloadConfig | None,
+        Field(description="CPU KV cache offload config for prefill nodes. None = disabled (NixlConnector only)."),
+    ] = None
+
     @property
     def num_nodes(self) -> int:
         return self.num_prefill_nodes + self.num_decode_nodes
@@ -322,6 +341,13 @@ class InferenceConfig(BaseConfig):
         ),
     ] = False

+    enable_dbo: Annotated[
+        bool,
+        Field(
+            description="Enable dual batch overlap (DBO). Passed to vLLM as `--enable-dbo`.",
+        ),
+    ] = False
+
     use_deep_gemm: Annotated[
         bool,
         Field(
@@ -468,6 +494,7 @@ def to_vllm(self) -> Namespace:
             "enable_expert_parallel": "enable_expert_parallel",
             "all2all_backend": "all2all_backend",
             "enable_eplb": "enable_eplb",
+            "enable_dbo": "enable_dbo",
             "seed": "seed",
         }

diff --git a/src/prime_rl/entrypoints/inference.py b/src/prime_rl/entrypoints/inference.py
index cae9bf3334..92ed6bc8af 100644
--- a/src/prime_rl/entrypoints/inference.py
+++ b/src/prime_rl/entrypoints/inference.py
@@ -60,6 +60,13 @@ def write_slurm_script(config: InferenceConfig, config_path: Path, script_path:
             use_deep_gemm=config.use_deep_gemm,
             prefill_env_overrides=config.deployment.prefill_env_overrides,
             decode_env_overrides=config.deployment.decode_env_overrides,
+            kv_offload=config.deployment.kv_cache_offload is not None,
+            kv_offload_block_size=config.deployment.kv_cache_offload.block_size
+            if config.deployment.kv_cache_offload
+            else 64,
+            kv_offload_cpu_bytes=int(config.deployment.kv_cache_offload.cpu_bytes)
+            if config.deployment.kv_cache_offload
+            else 0,
         )
     elif is_multi_node:
         template_vars.update(
diff --git a/src/prime_rl/entrypoints/rl.py b/src/prime_rl/entrypoints/rl.py
index 88cb6800da..47bee793f2 100644
--- a/src/prime_rl/entrypoints/rl.py
+++ b/src/prime_rl/entrypoints/rl.py
@@ -436,6 +436,9 @@ def write_slurm_script(config: RLConfig, config_dir: Path, script_path: Path) ->
             use_deep_gemm=config.inference.use_deep_gemm,
             prefill_env_overrides=infer_deploy.prefill_env_overrides,
             decode_env_overrides=infer_deploy.decode_env_overrides,
+            kv_offload=infer_deploy.kv_cache_offload is not None,
+            kv_offload_block_size=infer_deploy.kv_cache_offload.block_size if infer_deploy.kv_cache_offload else 64,
+            kv_offload_cpu_bytes=int(infer_deploy.kv_cache_offload.cpu_bytes) if infer_deploy.kv_cache_offload else 0,
             use_nccl_broadcast=config.weight_broadcast is not None and config.weight_broadcast.type == "nccl",
             wandb_shared=config.wandb is not None and config.wandb.shared,
             ranks_filter=",".join(map(str, config.trainer.log.ranks_filter)),
diff --git a/src/prime_rl/inference/patches.py b/src/prime_rl/inference/patches.py
index 18c6c3c021..a909f00ebf 100644
--- a/src/prime_rl/inference/patches.py
+++ b/src/prime_rl/inference/patches.py
@@ -1,3 +1,7 @@
+import torch
+from vllm.triton_utils import tl, triton
+
+
 def transformers_v5_compat():
     """vLLM general plugin: patch transformers v5 config attrs that vLLM 0.16 still expects.

@@ -10,9 +14,164 @@ def transformers_v5_compat():
         Qwen3VLMoeTextConfig.tie_word_embeddings = False

     _patch_qwen35_lora()
+    monkey_patch_deep_gemm_ep_scatter()
     monkey_patch_dp_engine_core_pause_resume_deadlock()


+@triton.jit
+def _apply_expert_map_triton(expert_id, expert_map):
+    if expert_id != -1:
+        expert_id = tl.load(expert_map + expert_id).to(expert_id.dtype)
+    return expert_id
+
+
+@triton.jit
+def _fwd_kernel_ep_scatter_2_int64(
+    total_token_num,
+    expert_start_loc,
+    recv_x,
+    recv_x_stride0,
+    recv_x_stride1,
+    recv_x_scale,
+    recv_x_scale_stride0,
+    recv_x_scale_stride1,
+    recv_topk,
+    recv_topk_stride0,
+    recv_topk_stride1,
+    output_tensor,
+    output_tensor_stride0,
+    output_tensor_stride1,
+    output_tensor_scale,
+    output_tensor_scale_stride0,
+    output_tensor_scale_stride1,
+    output_index,
+    output_index_stride0,
+    output_index_stride1,
+    topk_num: tl.constexpr,
+    expert_map,
+    HAS_EXPERT_MAP: tl.constexpr,
+    HIDDEN_SIZE: tl.constexpr,
+    HIDDEN_SIZE_PAD: tl.constexpr,
+    SCALE_HIDDEN_SIZE: tl.constexpr,
+    SCALE_HIDDEN_SIZE_PAD: tl.constexpr,
+):
+    start_token_id = tl.program_id(0)
+    grid_num = tl.num_programs(0)
+
+    offset_in = tl.arange(0, HIDDEN_SIZE_PAD)
+    mask = offset_in < HIDDEN_SIZE
+
+    offset_in_s = tl.arange(0, SCALE_HIDDEN_SIZE_PAD)
+    mask_s = offset_in_s < SCALE_HIDDEN_SIZE
+
+    output_tensor_stride0 = output_tensor_stride0.to(tl.int64)
+
+    for token_id in range(start_token_id, total_token_num, grid_num):
+        to_copy = tl.load(recv_x + token_id * recv_x_stride0 + offset_in, mask=mask)
+        to_copy_s = tl.load(
+            recv_x_scale + token_id * recv_x_scale_stride0 + offset_in_s,
+            mask=mask_s,
+        )
+
+        for topk_index in tl.range(0, topk_num, 1, num_stages=4):
+            expert_id = tl.load(recv_topk + token_id * recv_topk_stride0 + topk_index)
+
+            if HAS_EXPERT_MAP:
+                expert_id = _apply_expert_map_triton(expert_id, expert_map)
+
+            if expert_id >= 0:
+                dest_token_index = tl.atomic_add(expert_start_loc + expert_id, 1)
+                dest_token_index_i64 = dest_token_index.to(tl.int64)
+
+                tl.store(
+                    output_index + token_id * output_index_stride0 + topk_index,
+                    dest_token_index,
+                )
+
+                output_tensor_ptr = output_tensor + dest_token_index_i64 * output_tensor_stride0
+                output_tensor_scale_ptr = output_tensor_scale + dest_token_index * output_tensor_scale_stride0
+                tl.store(output_tensor_ptr + offset_in, to_copy, mask=mask)
+                tl.store(output_tensor_scale_ptr + offset_in_s, to_copy_s, mask=mask_s)
+
+
+def _triton_ep_scatter_int64(
+    recv_x: torch.Tensor,
+    recv_x_scale: torch.Tensor,
+    recv_topk: torch.Tensor,
+    num_recv_tokens_per_expert: torch.Tensor,
+    expert_map: torch.Tensor | None,
+    expert_start_loc: torch.Tensor,
+    output_tensor: torch.Tensor,
+    output_tensor_scale: torch.Tensor,
+    m_indices: torch.Tensor,
+    output_index: torch.Tensor,
+) -> None:
+    from vllm.model_executor.layers.fused_moe import deep_gemm_utils
+
+    block_e = 128
+    num_warps = 8
+    num_experts = num_recv_tokens_per_expert.shape[0]
+    hidden_size = recv_x.shape[1]
+
+    assert m_indices.shape[0] % block_e == 0
+    assert expert_start_loc.shape[0] == num_experts
+
+    deep_gemm_utils._fwd_kernel_ep_scatter_1[(num_experts,)](
+        num_recv_tokens_per_expert,
+        expert_start_loc,
+        m_indices,
+        num_experts=num_experts,
+        num_warps=num_warps,
+        BLOCK_E=block_e,
+        BLOCK_EXPERT_NUM=triton.next_power_of_2(num_experts),
+    )
+
+    grid = min(recv_topk.shape[0], 1024 * 8)
+    _fwd_kernel_ep_scatter_2_int64[(grid,)](
+        recv_topk.shape[0],
+        expert_start_loc,
+        recv_x,
+        recv_x.stride(0),
+        recv_x.stride(1),
+        recv_x_scale,
+        recv_x_scale.stride(0),
+        recv_x_scale.stride(1),
+        recv_topk,
+        recv_topk.stride(0),
+        recv_topk.stride(1),
+        output_tensor,
+        output_tensor.stride(0),
+        output_tensor.stride(1),
+        output_tensor_scale,
+        output_tensor_scale.stride(0),
+        output_tensor_scale.stride(1),
+        output_index,
+        output_index.stride(0),
+        output_index.stride(1),
+        topk_num=recv_topk.shape[1],
+        expert_map=expert_map,
+        HAS_EXPERT_MAP=expert_map is not None,
+        num_warps=num_warps,
+        HIDDEN_SIZE=hidden_size,
+        HIDDEN_SIZE_PAD=triton.next_power_of_2(hidden_size),
+        SCALE_HIDDEN_SIZE=recv_x_scale.shape[1],
+        SCALE_HIDDEN_SIZE_PAD=triton.next_power_of_2(recv_x_scale.shape[1]),
+    )
+
+
+def monkey_patch_deep_gemm_ep_scatter():
+    # Temporary local carry of the upstream fix while it is under review:
+    # issue: https://github.com/vllm-project/vllm/issues/39211
+    # PR:    https://github.com/vllm-project/vllm/pull/39213
+    from vllm.logger import init_logger
+    from vllm.model_executor.layers.fused_moe import deep_gemm_utils
+
+    logger = init_logger(__name__)
+
+    deep_gemm_utils.ep_scatter = torch.no_grad()(_triton_ep_scatter_int64)
+    logger.warning("Enabled int64-addressing Triton patch for vLLM DeepGEMM ep_scatter.")
+
+
 def _patch_qwen35_lora():
     """Fix Qwen3.5 LoRA: align packed_modules_mapping with output_sizes.

diff --git a/src/prime_rl/templates/inference.sbatch.j2 b/src/prime_rl/templates/inference.sbatch.j2
index 155bf45a0f..affd23860d 100644
--- a/src/prime_rl/templates/inference.sbatch.j2
+++ b/src/prime_rl/templates/inference.sbatch.j2
@@ -144,7 +144,12 @@ srun bash -c '
     export VLLM_NIXL_SIDE_CHANNEL_HOST=$LOCAL_IP
     export VLLM_NIXL_SIDE_CHANNEL_PORT=5600

-    KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
+{%- if kv_offload %}
+    PREFILL_KV_CFG='"'"'{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}},{"kv_connector":"OffloadingConnector","kv_role":"kv_both","kv_connector_extra_config":{"block_size":{{ kv_offload_block_size }},"cpu_bytes_to_use":{{ kv_offload_cpu_bytes }}}}]}}'"'"'
+{%- else %}
+    PREFILL_KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
+{%- endif %}
+    DECODE_KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
     DECODE_COMPILE_CFG='"'"'{"cudagraph_mode":"FULL_DECODE_ONLY"}'"'"'

     # Determine outer replica (P/D pair) and role
@@ -168,9 +173,9 @@ srun bash -c '
         ROLE_EXTRA="\"all2all_backend\": \"deepep_high_throughput\""

         if [ "$ROLE_RANK" -eq 0 ]; then
-            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $PREFILL_KV_CFG, $ROLE_EXTRA}"
         else
-            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $PREFILL_KV_CFG, $ROLE_EXTRA}"
         fi
     else
         # ── Decode node ──
@@ -190,9 +195,9 @@ srun bash -c '
         ROLE_EXTRA="\"all2all_backend\": \"deepep_low_latency\", \"compilation_config\": $DECODE_COMPILE_CFG"

         if [ "$ROLE_RANK" -eq 0 ]; then
-            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $DECODE_KV_CFG, $ROLE_EXTRA}"
         else
-            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $DECODE_KV_CFG, $ROLE_EXTRA}"
         fi
     fi

diff --git a/src/prime_rl/templates/multi_node_rl.sbatch.j2 b/src/prime_rl/templates/multi_node_rl.sbatch.j2
index 828841af62..f451502bee 100644
--- a/src/prime_rl/templates/multi_node_rl.sbatch.j2
+++ b/src/prime_rl/templates/multi_node_rl.sbatch.j2
@@ -203,7 +203,12 @@ if [ "$SLURM_PROCID" -lt "$NUM_INFER_NODES" ]; then
     export VLLM_NIXL_SIDE_CHANNEL_HOST=$LOCAL_IP
     export VLLM_NIXL_SIDE_CHANNEL_PORT=5600

-    KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
+{%- if kv_offload %}
+    PREFILL_KV_CFG='"'"'{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}},{"kv_connector":"OffloadingConnector","kv_role":"kv_both","kv_connector_extra_config":{"block_size":{{ kv_offload_block_size }},"cpu_bytes_to_use":{{ kv_offload_cpu_bytes }}}}]}}'"'"'
+{%- else %}
+    PREFILL_KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
+{%- endif %}
+    DECODE_KV_CFG='"'"'{"kv_connector":"NixlConnector","kv_role":"kv_both","kv_connector_extra_config":{"num_threads":1}}'"'"'
     DECODE_COMPILE_CFG='"'"'{"cudagraph_mode":"FULL_DECODE_ONLY"}'"'"'

     REPLICA_BASE=$((REPLICA_IDX * NODES_PER_INFER_REPLICA))
@@ -240,13 +245,23 @@ if [ "$SLURM_PROCID" -lt "$NUM_INFER_NODES" ]; then
         | tee -a $OUTPUT_DIR/logs/inference/node_${INFER_NODE_RANK}.log

     if [ "$DP" -gt 1 ]; then
+        if [ "$ROLE" = "prefill" ]; then
+            KV_CFG_TO_USE="$PREFILL_KV_CFG"
+        else
+            KV_CFG_TO_USE="$DECODE_KV_CFG"
+        fi
+
         if [ "$ROLE_RANK" -eq 0 ]; then
-            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$LOCAL_IP\", \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG_TO_USE, $ROLE_EXTRA}"
         else
-            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+            VLLM_EXTRA="{\"data_parallel_address\": \"$HEAD_HOST\", \"data_parallel_start_rank\": $START_RANK, \"data_parallel_hybrid_lb\": true, \"kv_transfer_config\": $KV_CFG_TO_USE, $ROLE_EXTRA}"
         fi
     else
-        VLLM_EXTRA="{\"kv_transfer_config\": $KV_CFG, $ROLE_EXTRA}"
+        if [ "$ROLE" = "prefill" ]; then
+            VLLM_EXTRA="{\"kv_transfer_config\": $PREFILL_KV_CFG, $ROLE_EXTRA}"
+        else
+            VLLM_EXTRA="{\"kv_transfer_config\": $DECODE_KV_CFG, $ROLE_EXTRA}"
+        fi
     fi

     # Start vllm-router on the first node of each replica (PD mode)

PATCH

echo "Patch applied successfully."
