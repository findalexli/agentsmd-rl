#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency check: if the raise ValueError is already present, skip
if grep -q 'max_num_seqs.*exceeds.*available Mamba cache blocks' vllm/v1/worker/gpu_model_runner.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/config/compilation.py b/vllm/config/compilation.py
index 5b6648908dd6..1d09e2b7de70 100644
--- a/vllm/config/compilation.py
+++ b/vllm/config/compilation.py
@@ -1279,58 +1279,6 @@ def adjust_cudagraph_sizes_for_spec_decode(
         self.max_cudagraph_capture_size = rounded_sizes[-1]
         self.cudagraph_capture_sizes = rounded_sizes

-    def adjust_cudagraph_sizes_for_mamba_cache(
-        self, num_mamba_cache_blocks: int
-    ) -> None:
-        """Cap cudagraph capture sizes to available Mamba cache blocks.
-
-        For hybrid Mamba/attention models, the Mamba conv_state and
-        ssm_state tensors have their first dimension equal to num_blocks
-        (from KVCacheConfig). During CUDA graph capture the decode batch
-        size equals num_tokens, so capture sizes exceeding num_blocks
-        would cause out-of-bounds access in Mamba kernels.
-
-        See: https://github.com/vllm-project/vllm/issues/34094
-        """
-        if not self.cudagraph_capture_sizes or num_mamba_cache_blocks <= 0:
-            return
-
-        assert self.max_cudagraph_capture_size is not None
-
-        if num_mamba_cache_blocks >= self.max_cudagraph_capture_size:
-            return
-
-        capped_sizes = [
-            s for s in self.cudagraph_capture_sizes if s <= num_mamba_cache_blocks
-        ]
-
-        if len(capped_sizes) == 0:
-            logger.warning(
-                "No valid cudagraph capture sizes remain after capping "
-                "to Mamba cache blocks (%d). The smallest capture size "
-                "was %d. Disabling cudagraph capture. Consider reducing "
-                "max_num_seqs or increasing available GPU memory.",
-                num_mamba_cache_blocks,
-                self.cudagraph_capture_sizes[0],
-            )
-            self.cudagraph_capture_sizes = []
-            self.max_cudagraph_capture_size = 0
-            return
-
-        logger.warning(
-            "Capping cudagraph capture sizes from max %d to %d to fit "
-            "Mamba cache blocks (%d blocks available). This limits the "
-            "maximum batch size that can use CUDA graphs. To increase "
-            "this limit, reduce max_num_seqs or increase available GPU "
-            "memory.",
-            self.max_cudagraph_capture_size,
-            capped_sizes[-1],
-            num_mamba_cache_blocks,
-        )
-
-        self.max_cudagraph_capture_size = capped_sizes[-1]
-        self.cudagraph_capture_sizes = capped_sizes
-
     def get_compile_ranges(self) -> list[Range]:
         """Get the compile ranges for the compilation config."""
         if self.compile_ranges_endpoints is None:
diff --git a/vllm/v1/worker/gpu_model_runner.py b/vllm/v1/worker/gpu_model_runner.py
index 8a43f43d0398..8cfa61baa599 100644
--- a/vllm/v1/worker/gpu_model_runner.py
+++ b/vllm/v1/worker/gpu_model_runner.py
@@ -5800,7 +5800,7 @@ def _init_minimal_kv_cache_for_profiling(self) -> None:
         )
         self.cache_config.num_gpu_blocks_override = saved_override

-        self.initialize_kv_cache(minimal_config)
+        self.initialize_kv_cache(minimal_config, is_profiling=True)
         self.cache_config.num_gpu_blocks = minimal_config.num_blocks

         logger.debug("Initialized minimal KV cache for CUDA graph profiling")
@@ -6121,7 +6121,11 @@ def _capture_cudagraphs(
             torch.accelerator.synchronize()
         self.maybe_remove_all_loras(self.lora_config)

-    def initialize_attn_backend(self, kv_cache_config: KVCacheConfig) -> None:
+    def initialize_attn_backend(
+        self,
+        kv_cache_config: KVCacheConfig,
+        is_profiling: bool = False,
+    ) -> None:
         """
         Initialize the attention backends and attention metadata builders.
         """
@@ -6193,7 +6197,9 @@ def create_attn_groups(

         # Resolve cudagraph_mode before actually initialize metadata_builders
         self._check_and_update_cudagraph_mode(
-            attention_backend_list, kv_cache_config.kv_cache_groups
+            attention_backend_list,
+            kv_cache_config.kv_cache_groups,
+            is_profiling=is_profiling,
         )

         # Check if attention backend supports PCP&DCP and related features.
@@ -6237,6 +6243,7 @@ def _check_and_update_cudagraph_mode(
         self,
         attention_backends: list[set[type[AttentionBackend]]],
         kv_cache_groups: list[KVCacheGroupSpec],
+        is_profiling: bool = False,
     ) -> None:
         """
         Resolve the cudagraph_mode when there are multiple attention
@@ -6377,21 +6384,29 @@ def _check_and_update_cudagraph_mode(
                 self.uniform_decode_query_len, self.parallel_config.tensor_parallel_size
             )

-        # If the model has Mamba layers and cudagraph mode includes FULL
-        # decode, cap cudagraph capture sizes to the number of available
-        # Mamba cache blocks. Each decode request needs one conv_state
-        # cache line, so capture batch sizes cannot exceed num_blocks.
-        # Only FULL decode graphs are affected because PIECEWISE captures
-        # run GDN/Mamba ops eagerly (prefill path, no causal_conv1d_update).
+        # For Mamba models with FULL decode cudagraphs, each decode
+        # sequence needs one Mamba cache block. The decode cudagraph
+        # dispatcher already caps batch sizes at max_num_seqs, so we just
+        # need to verify that enough blocks exist. Raising here instead
+        # of silently capping cudagraph_capture_sizes avoids unintended
+        # restrictions on PIECEWISE (prefill) cudagraphs.
         # See: https://github.com/vllm-project/vllm/issues/34094
-        if cudagraph_mode.has_full_cudagraphs():
+        if cudagraph_mode.has_full_cudagraphs() and not is_profiling:
             has_mamba = any(
                 isinstance(g.kv_cache_spec, MambaSpec) for g in kv_cache_groups
             )
             if has_mamba and self.kv_cache_config is not None:
-                self.compilation_config.adjust_cudagraph_sizes_for_mamba_cache(
-                    self.kv_cache_config.num_blocks
-                )
+                num_blocks = self.kv_cache_config.num_blocks
+                if self.max_num_reqs > num_blocks:
+                    raise ValueError(
+                        f"max_num_seqs ({self.max_num_reqs}) exceeds "
+                        f"available Mamba cache blocks ({num_blocks}). "
+                        f"Each decode sequence requires one Mamba cache "
+                        f"block, so CUDA graph capture cannot proceed. "
+                        f"Please lower max_num_seqs to at most "
+                        f"{num_blocks} or increase "
+                        f"gpu_memory_utilization."
+                    )

         # Trigger cudagraph dispatching keys initialization after
         # resolved cudagraph mode.
@@ -6752,7 +6767,11 @@ def maybe_add_kv_sharing_layers_to_kv_cache_groups(
                 else:
                     break

-    def initialize_kv_cache(self, kv_cache_config: KVCacheConfig) -> None:
+    def initialize_kv_cache(
+        self,
+        kv_cache_config: KVCacheConfig,
+        is_profiling: bool = False,
+    ) -> None:
         """
         Initialize KV cache based on `kv_cache_config`.
         Args:
@@ -6764,7 +6783,7 @@ def initialize_kv_cache(self, kv_cache_config: KVCacheConfig) -> None:
         self._mamba_copy_bufs = None
         self.may_add_encoder_only_layers_to_kv_cache_config()
         self.maybe_add_kv_sharing_layers_to_kv_cache_groups(kv_cache_config)
-        self.initialize_attn_backend(kv_cache_config)
+        self.initialize_attn_backend(kv_cache_config, is_profiling=is_profiling)
         # The kernel block size for all KV cache groups. For example, if
         # kv_cache_manager uses block_size 256 for a given group, but the attention
         # backends for that group only supports block_size 64, we will return

PATCH

echo "Patch applied successfully."
