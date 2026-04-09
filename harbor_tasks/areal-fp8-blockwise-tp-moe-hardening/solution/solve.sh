#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if grep -q 'def enabled(self) -> bool:' areal/api/cli_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index 0bfe77bca..a03921ba1 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -491,13 +491,17 @@ class ArchonFP8Config:
         },
     )

+    @property
+    def enabled(self) -> bool:
+        return self.mode != "disabled"
+
     def __post_init__(self):
         valid_modes = {"disabled", "blockwise"}
         if self.mode not in valid_modes:
             raise ValueError(
                 f"fp8_config.mode must be one of {valid_modes}, got {self.mode!r}"
             )
-        if self.mode != "disabled" and not self.use_triton:
+        if self.enabled and not self.use_triton:
             raise ValueError(
                 "fp8_config.use_triton must be True when FP8 is enabled. "
                 "torchao blockwise FP8 uses mixed per-operand scaling "
diff --git a/areal/experimental/engine/archon_checkpoint.py b/areal/experimental/engine/archon_checkpoint.py
index c3e05e51a..b09ae000a 100644
--- a/areal/experimental/engine/archon_checkpoint.py
+++ b/areal/experimental/engine/archon_checkpoint.py
@@ -322,6 +322,37 @@ def _consolidate_and_cleanup(process_group=consolidation_pg):
         dist.barrier(group=engine.cpu_group)


+def _check_fp8_shard_compatibility(
+    hf_state_dict: dict[str, torch.Tensor],
+    scale_keys: list[str],
+) -> None:
+    """Fail fast if any FP8 weight has non-Shard(0) DTensor placement.
+
+    Must be called before ``_prepare_fp8_state_dict`` / ``dcp.load`` to
+    avoid wasting DCP I/O on a configuration that will fail at dequant.
+    """
+    try:
+        from torch.distributed.tensor import DTensor
+        from torch.distributed.tensor.placement_types import Shard
+    except ImportError:
+        return
+
+    for scale_key in scale_keys:
+        weight_key = scale_key.replace("_scale_inv", "")
+        weight = hf_state_dict.get(weight_key)
+        if weight is None or not isinstance(weight, DTensor):
+            continue
+        for p in weight.placements:
+            if isinstance(p, Shard) and p.dim != 0:
+                raise ValueError(
+                    f"FP8 checkpoint loading does not yet support "
+                    f"column-sharded weights (TP/ETP). Weight "
+                    f"{weight_key!r} has placements {weight.placements}. "
+                    f"Use TP=1 for FP8 checkpoint loading, or wait for "
+                    f"Shard(1) dequantization support (Phase 2)."
+                )
+
+
 def load_model_from_hf(engine: ArchonEngine, path: str) -> None:
     """Load model from HuggingFace format using DCP infrastructure."""
     _validate_model_initialized(engine)
@@ -362,6 +393,7 @@ def load_model_from_hf(engine: ArchonEngine, path: str) -> None:
             hf_state_dict[embed_key] = torch.empty_like(state_dict["output.weight"])

     if _is_fp8_ckpt:
+        _check_fp8_shard_compatibility(hf_state_dict, _fp8_scale_keys)
         hf_state_dict = _prepare_fp8_state_dict(
             hf_state_dict, path, _cached_keys=_fp8_scale_keys
         )
diff --git a/areal/experimental/engine/archon_engine.py b/areal/experimental/engine/archon_engine.py
index b41564040..3b0242ac4 100644
--- a/areal/experimental/engine/archon_engine.py
+++ b/areal/experimental/engine/archon_engine.py
@@ -300,7 +300,7 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
         # This assertion covers the training path (Phase 1A): blockwise FP8 matmuls
         # require BF16 master weights. Loading an FP8 checkpoint into a BF16 model
         # (Phase 1B, archon_checkpoint.py) is a separate path and may relax this.
-        if self.config.archon.fp8_config.mode != "disabled":
+        if self.config.archon.fp8_config.enabled:
             if self.config.dtype != "bfloat16":
                 raise ValueError(
                     f"FP8 training requires dtype=bfloat16 (master weights), "
@@ -342,7 +342,7 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
             f"Applied parallelism in {time.perf_counter() - tik:.2f} seconds"
         )

-        if self.config.archon.fp8_config.mode != "disabled":
+        if self.config.archon.fp8_config.enabled:
             from areal.experimental.models.archon.fp8 import (
                 validate_fp8_shard_alignment,
             )
diff --git a/areal/experimental/engine/archon_utils.py b/areal/experimental/engine/archon_utils.py
index 05ea09424..eddeeed68 100644
--- a/areal/experimental/engine/archon_utils.py
+++ b/areal/experimental/engine/archon_utils.py
@@ -330,7 +330,7 @@ def prepare_training_config(
         ac_config=ac_config,
         logger=logger,
     )
-    if config.archon.fp8_config.mode != "disabled" and enable_compile:
+    if config.archon.fp8_config.enabled and enable_compile:
         logger.warning(
             "FP8 blockwise training is incompatible with torch.compile. "
             "Disabling torch.compile."
diff --git a/areal/experimental/models/archon/fp8.py b/areal/experimental/models/archon/fp8.py
index c4279b152..3874c920f 100644
--- a/areal/experimental/models/archon/fp8.py
+++ b/areal/experimental/models/archon/fp8.py
@@ -99,6 +99,7 @@ def _patch_fp8_experts_forward(mod: nn.Module, use_triton: bool) -> None:
     )

     mod._fp8_use_triton = use_triton  # type: ignore[attr-defined]
+    mod._fp8_block = _FP8_BLOCK  # type: ignore[attr-defined]

     def _fp8_expert_fwd(
         self: nn.Module,
@@ -147,8 +148,11 @@ def _fp8_linear_fwd(self: nn.Linear, x: torch.Tensor) -> torch.Tensor:
         pad = (self._fp8_block - m % self._fp8_block) % self._fp8_block
         if pad > 0:
             x = F.pad(x, (0, 0, 0, pad))
+        weight = self.weight
+        if hasattr(weight, "to_local"):
+            weight = weight.to_local()
         out = self._fp8_mm.apply(
-            x, self.weight, self._fp8_block, x.dtype, self._fp8_use_triton
+            x, weight, self._fp8_block, x.dtype, self._fp8_use_triton
         )
         if pad > 0:
             out = out[:m]
@@ -168,31 +172,57 @@ def validate_fp8_shard_alignment(
     multiples of ``block_size``.  The FP8 kernel pads the token (M)
     dimension automatically, but weight dimensions (N, K) must be
     pre-aligned — a mismatch causes a Triton/cuBLAS crash at runtime.
+
+    Validates both ``nn.Linear`` modules (2D weights) and
+    ``GroupedExperts`` modules (3D weights ``[num_experts, dim_a, dim_b]``
+    where each per-expert slice must be block-aligned).
     """
+    from areal.experimental.models.archon.moe.grouped_experts import GroupedExperts
+
     try:
         from torch.distributed.tensor import DTensor
     except ImportError:
         DTensor = None  # type: ignore[assignment, misc]

+    def _local_shape(t: torch.Tensor) -> torch.Size:
+        if DTensor is not None and isinstance(t, DTensor):
+            return t.to_local().shape
+        return t.shape
+
     for part in model_parts:
         for fqn, mod in part.named_modules():
-            if not isinstance(mod, nn.Linear):
-                continue
             if not hasattr(mod, "_fp8_block"):
                 continue

-            weight = mod.weight
-            if DTensor is not None and isinstance(weight, DTensor):
-                local_shape = weight._local_tensor.shape
-            else:
-                local_shape = weight.shape
-
-            out_dim, in_dim = local_shape[0], local_shape[1]
-            if out_dim % block_size != 0 or in_dim % block_size != 0:
-                raise ValueError(
-                    f"FP8 module {fqn!r} has non-{block_size}-aligned local "
-                    f"weight shape {tuple(local_shape)} after parallelism. "
-                    f"This will cause FP8 kernel failures at runtime. "
-                    f"Adjust TP degree or add this module's name to "
-                    f"fp8_config.exclude_modules."
-                )
+            # --- nn.Linear: 2D weight (out_dim, in_dim) ---
+            if isinstance(mod, nn.Linear):
+                local_shape = _local_shape(mod.weight)
+                out_dim, in_dim = local_shape[0], local_shape[1]
+                if out_dim % block_size != 0 or in_dim % block_size != 0:
+                    raise ValueError(
+                        f"FP8 module {fqn!r} has non-{block_size}-aligned "
+                        f"local weight shape {tuple(local_shape)} after "
+                        f"parallelism. This will cause FP8 kernel failures "
+                        f"at runtime. Adjust TP degree or add this module's "
+                        f"name to fp8_config.exclude_modules."
+                    )
+
+            # --- GroupedExperts: 3D weights (num_experts, dim_a, dim_b) ---
+            elif isinstance(mod, GroupedExperts):
+                for wname in ("w1", "w2", "w3"):
+                    w = getattr(mod, wname, None)
+                    if w is None:
+                        continue
+                    local_shape = _local_shape(w)
+                    # Per-expert slice is (dim_a, dim_b); both must be aligned.
+                    dim_a, dim_b = local_shape[1], local_shape[2]
+                    if dim_a % block_size != 0 or dim_b % block_size != 0:
+                        raise ValueError(
+                            f"FP8 expert {fqn!r}.{wname} has non-"
+                            f"{block_size}-aligned local per-expert shape "
+                            f"({dim_a}, {dim_b}) (full local shape "
+                            f"{tuple(local_shape)}) after parallelism. "
+                            f"This will cause FP8 kernel failures at "
+                            f"runtime. Adjust TP/ETP degree or disable "
+                            f"fp8_config.include_experts."
+                        )
diff --git a/areal/experimental/models/archon/fp8_checkpoint.py b/areal/experimental/models/archon/fp8_checkpoint.py
index c2ac8bc58..d5096eeb8 100644
--- a/areal/experimental/models/archon/fp8_checkpoint.py
+++ b/areal/experimental/models/archon/fp8_checkpoint.py
@@ -165,6 +165,10 @@ def _dequant_dtensor(
     )
     from torch.distributed.tensor.placement_types import Shard

+    # TODO(agent): Implement per-column scale slicing for Shard(1) to
+    #   support TP/ETP FP8 checkpoint loading. Requires slicing scale_inv
+    #   along dim-1 with block-boundary alignment (mirrors the dim-0 logic
+    #   below). Tracked as Phase 2 of FP8 support.
     for p in weight_fp8.placements:
         if isinstance(p, Shard) and p.dim != 0:
             raise ValueError(
@@ -251,12 +255,7 @@ def dequant_fp8_state_dict(
     Raises:
         KeyError: If a FP8 weight has no matching ``*_scale_inv`` key.
     """
-    fp8_dtypes = {
-        torch.float8_e4m3fn,
-        torch.float8_e5m2,
-        torch.float8_e4m3fnuz,
-        torch.float8_e5m2fnuz,
-    }
+    fp8_dtypes = {torch.float8_e4m3fn}

     fp8_keys = [
         k
diff --git a/examples/math/gsm8k_sft_archon_fp8.yaml b/examples/math/gsm8k_sft_archon_fp8.yaml
index 0e8a194c4..5c08d4008 100644
--- a/examples/math/gsm8k_sft_archon_fp8.yaml
+++ b/examples/math/gsm8k_sft_archon_fp8.yaml
@@ -39,6 +39,7 @@ actor:
   archon:
     fp8_config:
       mode: blockwise
+      # exclude_modules: [output, router, score]  # default; YAML replaces entire list
   scheduling_spec:
     - task_type: worker
       port_count: 2

PATCH

echo "Patch applied successfully."
