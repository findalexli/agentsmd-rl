#!/usr/bin/env bash
set -euo pipefail

cd /workspace/areal

# Idempotency: if the gold change is already present, skip.
if grep -q 'reshard_after_forward_policy' areal/api/cli_args.py 2>/dev/null \
   && grep -q 'is_moe_model_config' areal/experimental/models/archon/utils.py 2>/dev/null; then
    echo "Gold patch already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.gitignore b/.gitignore
index 0ad86d3d3f..3f7738f902 100644
--- a/.gitignore
+++ b/.gitignore
@@ -13,6 +13,7 @@

 # opencode
 .opencode/sessions/
+.sisyphus/

 # Ruff
 .ruff_cache/
diff --git a/AGENTS.md b/AGENTS.md
index 5cffe95581..c6276c74cc 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -9,6 +9,7 @@
 ```bash
 # Environment
 uv sync --extra cuda            # dependencies (or `uv sync` without CUDA)
+source .venv/bin/activate        # activate venv BEFORE pre-commit or git commit if venv exists
 pre-commit install               # formatting hooks (Ruff, mdformat, clang-format, nbstripout, autoflake)
 pre-commit run --all-files       # lint + format everything

diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index 7a502be119..808d95811f 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -489,6 +489,18 @@ class ArchonEngineConfig:
         },
     )

+    # FSDP reshard policy after forward pass
+    reshard_after_forward_policy: str = field(
+        default="default",
+        metadata={
+            "help": "FSDP reshard policy after forward pass. "
+            "'default': reshard when pipeline parallelism is off; keep unsharded when on to avoid repeated all-gather per microbatch. "
+            "'always': always reshard after forward (saves memory). "
+            "'never': never reshard after forward.",
+            "choices": ["default", "always", "never"],
+        },
+    )
+
     # Deterministic mode
     use_deterministic_algorithms: bool = field(
         default=False,
@@ -515,6 +527,12 @@ def __post_init__(self):
                 f"pp_last_stage_less_layers must be >= 0, "
                 f"got {self.pp_last_stage_less_layers}"
             )
+        valid_reshard_policies = ("default", "always", "never")
+        if self.reshard_after_forward_policy not in valid_reshard_policies:
+            raise ValueError(
+                f"reshard_after_forward_policy must be one of {valid_reshard_policies}, "
+                f"got '{self.reshard_after_forward_policy}'"
+            )


 # These configurations are used by Megatron Bridge to build Megatron models.
diff --git a/areal/experimental/engine/archon_engine.py b/areal/experimental/engine/archon_engine.py
index e6552ba94a..50b3d4f4ac 100644
--- a/areal/experimental/engine/archon_engine.py
+++ b/areal/experimental/engine/archon_engine.py
@@ -74,6 +74,7 @@
     ulysses_gather_output,
     ulysses_slice_inputs,
 )
+from areal.experimental.models.archon.utils import is_moe_model_config
 from areal.infra.dist_rollout import DistRolloutCoordinator
 from areal.infra.platforms import current_platform
 from areal.models.tree_attn.functional import (
@@ -292,13 +293,18 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
         ac_config = self._build_ac_config()
         enable_compile = self.config.archon.enable_compile

+        # NOTE: Upgrading PyTorch may resolve these in the future.
         # Zero-bubble schedules (InterleavedZeroBubble, ZBVZeroBubble, DualPipeV)
-        # use split backward (I/W steps). This is incompatible with:
-        # 1. torch.compile - donated buffer optimization assumes a single
-        #    backward pass (retain_graph=False).
-        # 2. Op-level selective AC - its per-op cache (storage.pop) is consumed
+        # use split backward (I/W steps) with retain_graph=True between them.
+        # This is incompatible with:
+        # 1. torch.compile - disabled unconditionally for zero-bubble.
+        # 2. donated_buffer (MoE only) - MoE models have internally compiled
+        #    ops (via AOTAutograd) whose backward uses donated buffers. These
+        #    are freed after backward, conflicting with retain_graph=True.
+        #    Dense models have no such ops and are unaffected.
+        # 3. Op-level selective AC - its per-op cache (storage.pop) is consumed
         #    by the I step, leaving nothing for the W step recompute.
-        # 3. memory_budget AC - it depends on torch.compile.
+        # 4. memory_budget AC - it depends on torch.compile.
         # Full AC / layer-level selective AC use standard checkpoint_wrapper
         # whose gid-based recompute supports multiple backward passes.
         schedule_class = get_schedule_class(self.config.archon.pp_schedule)
@@ -316,6 +322,22 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
                 )
                 enable_compile = False

+            # NOTE: Upgrading PyTorch may resolve this in the future.
+            # MoE models have internally compiled ops (via AOTAutograd)
+            # whose backward uses donated buffers - these conflict with
+            # retain_graph=True in split backward. Dense models have no
+            # such ops and are unaffected.
+            if is_moe_model_config(self.model_config):
+                import torch._functorch.config as functorch_config
+
+                if getattr(functorch_config, "donated_buffer", False):
+                    self.logger.info(
+                        f"{schedule_name} requires donated_buffer=False "
+                        "for MoE models (internally compiled ops conflict "
+                        "with retain_graph=True in split backward). Disabling."
+                    )
+                    functorch_config.donated_buffer = False
+
             if ac_config is not None and (
                 (
                     ac_config.mode == "selective"
@@ -899,7 +921,7 @@ def _apply_pipeline_parallelism(
             reduce_dtype=torch.float32,
             loss_parallel=True,
             cpu_offload=self.config.archon.offload_params,
-            reshard_after_forward_policy="default",
+            reshard_after_forward_policy=self.config.archon.reshard_after_forward_policy,
             ac_config=ac_config,
             enable_compile=enable_compile,
         )
@@ -938,7 +960,7 @@ def _apply_parallelism(
             reduce_dtype=torch.float32,
             loss_parallel=True,
             cpu_offload=self.config.archon.offload_params,
-            reshard_after_forward_policy="default",
+            reshard_after_forward_policy=self.config.archon.reshard_after_forward_policy,
             ac_config=ac_config,
             enable_compile=enable_compile,
         )
@@ -1239,16 +1261,20 @@ def _prepare_mb_list(self, input_: dict[str, Any]) -> MicroBatchList:

         input_ = amend_position_ids(input_)

-        # Pipeline parallelism requires n_microbatches >= pp_stages
+        # Pipeline parallelism requires n_microbatches >= num_total_stages
         if self.parallel_dims.pp_enabled:
             pp_size = self.parallel_dims.pp
+            stages_per_rank = len(self.pp_stages)
+            num_total_stages = pp_size * stages_per_rank
             n_seqs = input_["attention_mask"].shape[0]
-            if n_seqs < pp_size:
+            if n_seqs < num_total_stages:
                 raise RuntimeError(
-                    f"Pipeline parallelism requires at least {pp_size} sequences, "
-                    f"but got {n_seqs}. Increase batch size or reduce PP degree."
+                    f"Pipeline parallelism requires at least {num_total_stages} "
+                    f"sequences (pp_size={pp_size} * stages_per_rank="
+                    f"{stages_per_rank}), but got {n_seqs}. "
+                    f"Increase batch size or reduce PP degree/stages."
                 )
-            min_n_mbs = pp_size
+            min_n_mbs = num_total_stages
             mb_spec = MicroBatchSpec.new(
                 self.config.mb_spec,
                 n_mbs=max(min_n_mbs, self.config.mb_spec.n_mbs or 1),
diff --git a/areal/experimental/engine/archon_runner.py b/areal/experimental/engine/archon_runner.py
index 1415f3c280..b9f37c87d4 100644
--- a/areal/experimental/engine/archon_runner.py
+++ b/areal/experimental/engine/archon_runner.py
@@ -20,6 +20,11 @@
 logger = logging.getLogger("ArchonRunner")


+class _NullOutputChunks(list):
+    def append(self, item: Any) -> None:
+        pass
+
+
 class ForwardBackwardRunner(ABC):
     """Abstract base for forward/backward execution strategies."""

@@ -216,9 +221,11 @@ def _run_eval(
         if not self.has_last_stage:
             return None
         output_stage = self._get_output_stage()
-        return self._process_outputs(
+        results = self._process_outputs(
             output_stage.output_chunks, contexts, process_output_fn
         )
+        output_stage.output_chunks.clear()
+        return results

     def _run_train(
         self,
@@ -232,7 +239,24 @@ def _run_train(
         pp_loss_fn = self._create_loss_fn(contexts, process_output_fn)
         schedule = self._create_schedule(n_microbatches, loss_fn=pp_loss_fn)
         self._patch_skip_output_merge(schedule)
+
+        # NOTE: Upgrading PyTorch may resolve this in the future.
+        # Replace output_chunks with a null list so
+        # forward_one_chunk's `output_chunks.append(output)` becomes a no-op.
+        # (torch/distributed/pipelining/schedules.py)
+        # This lets each microbatch's logits be freed right after its backward,
+        # instead of holding all N sets of logits until step() returns.
+        output_stage = None
+        if self.has_last_stage:
+            output_stage = self._get_output_stage()
+            output_stage.output_chunks = _NullOutputChunks()
+
         schedule.step(*args, target=batched_target, **batched_kwargs)
+
+        # Restore normal list so subsequent eval() calls on the same
+        # stage can read output_chunks normally.
+        if output_stage is not None:
+            output_stage.output_chunks = []
         return []

     def _create_loss_fn(
diff --git a/areal/experimental/models/archon/utils.py b/areal/experimental/models/archon/utils.py
index 72e56bdc84..ecb0b06d71 100644
--- a/areal/experimental/models/archon/utils.py
+++ b/areal/experimental/models/archon/utils.py
@@ -137,9 +137,29 @@ def validate_ep_constraints(
         )


+def is_moe_model_config(model_config: object) -> bool:
+    """Check if a HuggingFace PretrainedConfig represents a Mixture-of-Experts model.
+
+    Inspects common HF config attributes (num_experts, num_local_experts)
+    to determine whether the model uses MoE layers.
+
+    Args:
+        model_config: A HuggingFace PretrainedConfig (or any object with
+            num_experts / num_local_experts attributes).
+
+    Returns:
+        True if the config indicates an MoE model with more than one expert.
+    """
+    num_experts = getattr(model_config, "num_experts", None)
+    if num_experts is None:
+        num_experts = getattr(model_config, "num_local_experts", None)
+    return num_experts is not None and num_experts > 1
+
+
 __all__ = [
     "ModelArgsProtocol",
     "MoEModelArgsProtocol",
+    "is_moe_model_config",
     "validate_cp_constraints",
     "validate_tp_constraints",
     "validate_ep_constraints",
diff --git a/docs/best_practices/handling_oom.md b/docs/best_practices/handling_oom.md
index 06a56d2702..29e7866530 100644
--- a/docs/best_practices/handling_oom.md
+++ b/docs/best_practices/handling_oom.md
@@ -144,6 +144,14 @@ allocation_mode: sglang:d4+archon:d2p2e2
 We recommend pipeline and expert parallelism over tensor/context parallelism. Check
 [Allocation Mode Reference](../reference/alloc_mode.md) for more details.

+```{seealso}
+Pipeline parallelism introduces unique memory challenges (microbatch warmup accumulation,
+zero-bubble `retain_graph` overhead, FSDP resharding trade-offs, gradient accumulation
+costs, and per-rank memory budgeting). See the
+[Archon PP Memory Guide](../tutorial/archon.md#appendix-pipeline-parallelism-memory-guide)
+for a comprehensive walkthrough.
+```
+
 ### 4. Switch to a Lightweight Optimizer

 AReaL supports different optimizers depending on the training engine.
diff --git a/docs/cli_reference.md b/docs/cli_reference.md
index 99e46db292..b63d0ab623 100644
--- a/docs/cli_reference.md
+++ b/docs/cli_reference.md
@@ -785,21 +785,22 @@ Configuration for Weights & Biases experiment tracking.

 Configuration for Archon Engine training backend.

-| Parameter                      | Type            | Default             | Description                                                                                                                                                                                                                                                          |
-| ------------------------------ | --------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
-| `attn_type`                    | string          | `"varlen"`          | Attention backend type. Use 'tree' for tree training. **Choices:** `varlen`, `sdpa`, `tree`                                                                                                                                                                          |
-| `offload_params`               | boolean         | `False`             | Whether to offload FSDP parameters to CPU.                                                                                                                                                                                                                           |
-| `enable_compile`               | boolean         | `True`              | Enable torch.compile for TransformerBlocks.                                                                                                                                                                                                                          |
-| `ac_mode`                      | string          | `"selective"`       | Activation checkpointing mode. 'memory_budget' requires enable_compile=True. **Choices:** `none`, `full`, `selective`, `memory_budget`                                                                                                                               |
-| `selective_ac_option`          | string          | `"op"`              | Selective AC option: 'op' for op-level, or integer string (e.g., '2') for every Nth layer.                                                                                                                                                                           |
-| `ac_memory_budget`             | float           | `0.5`               | Memory budget for 'memory_budget' AC mode. 0.0 = minimum memory (max recompute), 1.0 = default behavior (no recompute).                                                                                                                                              |
-| `ac_preserve_rng_state`        | boolean         | `False`             | Preserve RNG state during checkpointing for deterministic output. Enabling this may slow down training.                                                                                                                                                              |
-| `ac_debug`                     | boolean         | `False`             | (Testing only) Capture AC debug information. Will be slower.                                                                                                                                                                                                         |
-| `pp_schedule`                  | string          | `"Interleaved1F1B"` | Pipeline parallel schedule type. **Choices:** `1F1B`, `Interleaved1F1B`, `InterleavedZeroBubble`, `ZBVZeroBubble`                                                                                                                                                    |
-| `pp_layers_per_stage`          | integer \| None | `None`              | Number of transformer layers per (virtual) pipeline stage. If set, num_virtual_stages is calculated from num_layers. If None, stages are inferred from schedule type (1 stage/rank for 1F1B, 2 stages/rank for Interleaved1F1B/InterleavedZeroBubble/ZBVZeroBubble). |
-| `pp_first_stage_less_layers`   | integer         | `1`                 | Number of layers to reduce in the first pipeline stage. Accounts for embedding layer overhead.                                                                                                                                                                       |
-| `pp_last_stage_less_layers`    | integer         | `1`                 | Number of layers to reduce in the last pipeline stage. Accounts for output layer overhead.                                                                                                                                                                           |
-| `use_deterministic_algorithms` | boolean         | `False`             | Enable deterministic algorithms for training reproducibility. Sets torch.use_deterministic_algorithms(True, warn_only=True), CUBLAS_WORKSPACE_CONFIG, NCCL_ALGO, and TORCH_COMPILE_DETERMINISTIC. May reduce performance.                                            |
+| Parameter                      | Type            | Default             | Description                                                                                                                                                                                                                                                                                             |
+| ------------------------------ | --------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `attn_type`                    | string          | `"varlen"`          | Attention backend type. Use 'tree' for tree training. **Choices:** `varlen`, `sdpa`, `tree`                                                                                                                                                                                                             |
+| `offload_params`               | boolean         | `False`             | Whether to offload FSDP parameters to CPU.                                                                                                                                                                                                                                                              |
+| `enable_compile`               | boolean         | `True`              | Enable torch.compile for TransformerBlocks.                                                                                                                                                                                                                                                             |
+| `ac_mode`                      | string          | `"selective"`       | Activation checkpointing mode. 'memory_budget' requires enable_compile=True. **Choices:** `none`, `full`, `selective`, `memory_budget`                                                                                                                                                                  |
+| `selective_ac_option`          | string          | `"op"`              | Selective AC option: 'op' for op-level, or integer string (e.g., '2') for every Nth layer.                                                                                                                                                                                                              |
+| `ac_memory_budget`             | float           | `0.5`               | Memory budget for 'memory_budget' AC mode. 0.0 = minimum memory (max recompute), 1.0 = default behavior (no recompute).                                                                                                                                                                                 |
+| `ac_preserve_rng_state`        | boolean         | `False`             | Preserve RNG state during checkpointing for deterministic output. Enabling this may slow down training.                                                                                                                                                                                                 |
+| `ac_debug`                     | boolean         | `False`             | (Testing only) Capture AC debug information. Will be slower.                                                                                                                                                                                                                                            |
+| `pp_schedule`                  | string          | `"Interleaved1F1B"` | Pipeline parallel schedule type. **Choices:** `1F1B`, `Interleaved1F1B`, `InterleavedZeroBubble`, `ZBVZeroBubble`                                                                                                                                                                                       |
+| `pp_layers_per_stage`          | integer \| None | `None`              | Number of transformer layers per (virtual) pipeline stage. If set, num_virtual_stages is calculated from num_layers. If None, stages are inferred from schedule type (1 stage/rank for 1F1B, 2 stages/rank for Interleaved1F1B/InterleavedZeroBubble/ZBVZeroBubble).                                    |
+| `pp_first_stage_less_layers`   | integer         | `1`                 | Number of layers to reduce in the first pipeline stage. Accounts for embedding layer overhead.                                                                                                                                                                                                          |
+| `pp_last_stage_less_layers`    | integer         | `1`                 | Number of layers to reduce in the last pipeline stage. Accounts for output layer overhead.                                                                                                                                                                                                              |
+| `reshard_after_forward_policy` | string          | `"default"`         | FSDP reshard policy after forward pass. 'default': reshard when pipeline parallelism is off; keep unsharded when on to avoid repeated all-gather per microbatch. 'always': always reshard after forward (saves memory). 'never': never reshard after forward. **Choices:** `default`, `always`, `never` |
+| `use_deterministic_algorithms` | boolean         | `False`             | Enable deterministic algorithms for training reproducibility. Sets torch.use_deterministic_algorithms(True, warn_only=True), CUBLAS_WORKSPACE_CONFIG, NCCL_ALGO, and TORCH_COMPILE_DETERMINISTIC. May reduce performance.                                                                               |

 (section-distributed-data-parallel)=

diff --git a/docs/tutorial/archon.md b/docs/tutorial/archon.md
index b327c36075..e17de945c8 100644
--- a/docs/tutorial/archon.md
+++ b/docs/tutorial/archon.md
@@ -136,6 +136,7 @@ Archon-specific options are configured under `actor.archon.*`:
 | `enable_compile`               | `True`            | Enable torch.compile                                                          |
 | `ac_mode`                      | `selective`       | Activation checkpointing mode                                                 |
 | `offload_params`               | `False`           | Offload FSDP parameters to CPU                                                |
+| `reshard_after_forward_policy` | `default`         | FSDP reshard after forward (`default`/`always`/`never`)                       |
 | `use_deterministic_algorithms` | `False`           | Deterministic training for reproducibility (see [below](#deterministic-mode)) |

 See [Performance Tuning](#performance-tuning) for detailed guidance on these options.
@@ -350,3 +351,177 @@ python3 examples/math/gsm8k_rl.py --config archon_qwen3_moe.yaml
   mode syntax
 - [Fine-tuning Large MoE Models](megatron.md) - MegatronEngine alternative for MoE
   models
+
+## Appendix: Pipeline Parallelism Memory Guide
+
+Pipeline parallelism (PP) in the Archon engine introduces unique memory challenges
+compared to pure data parallelism. This appendix explains the root causes and practical
+mitigations.
+
+### A.1 Microbatch Count and Warmup Accumulation
+
+Interleaved PP schedules (e.g., `Interleaved1F1B`, `InterleavedZeroBubble`) have a
+**warmup phase** that accumulates multiple forward passes before any backward pass runs.
+When `n_microbatches < num_total_stages`, most or all forward passes pile up before the
+first backward, causing peak GPU memory to spike far beyond what the steady-state 1F1B
+phase requires.
+
+For example, with `pp_size=2` and `stages_per_rank=2` (`num_total_stages=4`):
+
+| `mb_spec.n_mbs` | Actual microbatches          | Warmup forwards (rank 0) | Peak activation sets    | Per-set size |
+| --------------- | ---------------------------- | ------------------------ | ----------------------- | ------------ |
+| 1 (default)     | 2 (auto-raised to `pp_size`) | 3                        | 4 (all before backward) | `batch / 2`  |
+| 4 (recommended) | 4                            | 3                        | 4 (transient)           | `batch / 4`  |
+| 8               | 8                            | 3                        | 4 (transient)           | `batch / 8`  |
+
+While the peak count of in-flight activation sets stays the same (~`num_total_stages`),
+each set shrinks proportionally with more microbatches.
+
+**Fix:** Set `mb_spec.n_mbs` to at least `num_total_stages`:
+
+```yaml
+actor:
+  mb_spec:
+    n_mbs: 4  # >= pp_size * stages_per_rank
+```
+
+```{note}
+AReaL automatically raises `n_mbs` to `num_total_stages` when it is too low and logs a
+warning. To silence the warning and ensure optimal splitting, set `n_mbs` explicitly.
+```
+
+### A.2 Zero Bubble Schedules and `retain_graph`
+
+Zero bubble schedules (`InterleavedZeroBubble`, `ZBVZeroBubble`, `DualPipeV`) split each
+backward pass into two phases:
+
+- **I step** (`stage_backward_input`): computes input gradients with `retain_graph=True`
+- **W step** (`stage_backward_weight`): computes weight gradients, then releases the
+  graph
+
+The I step must keep the forward computation graph alive (`retain_graph=True`) because
+the W step still needs it. This single design choice cascades into several memory
+penalties:
+
+| Consequence                    | Why                                                                   | Memory impact                                |
+| ------------------------------ | --------------------------------------------------------------------- | -------------------------------------------- |
+| Activations live longer        | Graph between I->W cannot be freed                                    | +15--20 GB (model-dependent)                 |
+| `donated_buffer` disabled      | Donated buffers are freed after backward, conflicts with retain_graph | Backward temp buffers cannot be reused       |
+| `torch.compile` disabled       | Compile's donated buffer optimization has the same conflict           | Lose Inductor memory optimizations           |
+| Op-level selective AC unusable | Per-op cache is consumed by I step, nothing left for W step           | Must use full AC or layer-level selective AC |
+
+Non-zero-bubble schedules (`1F1B`, `Interleaved1F1B`) perform backward in a single pass
+without `retain_graph=True`, so **none of these penalties apply**. If memory is tight
+and you do not need zero-bubble throughput, switching to `Interleaved1F1B` is the
+simplest mitigation:
+
+```yaml
+actor:
+  archon:
+    pp_schedule: Interleaved1F1B  # no split backward, no retain_graph overhead
+```
+
+If you need zero-bubble throughput but IZB causes OOM, **try `ZBVZeroBubble` first**.
+ZBV uses a V-shape stage assignment that is significantly more memory-friendly than
+IZB's interleaved assignment:
+
+|                         | IZB (interleaved)    | ZBV (V-shape)            |
+| ----------------------- | -------------------- | ------------------------ |
+| Rank 0 stages (4 total) | \[0, 2\] (same side) | \[0, 3\] (opposite ends) |
+| Rank 1 stages (4 total) | \[1, 3\] (same side) | \[1, 2\] (opposite ends) |
+
+The V-shape co-locates the first and last pipeline stages on the same rank. This matters
+because the last stage produces the loss directly -- its backward can start
+**immediately** after forward with no cross-rank communication. In ZBV's warmup, chunk1
+activations follow an `F->I->W` pattern where each activation is created and freed
+locally, never piling up.
+
+IZB's interleaved assignment places all of a rank's stages on the same side of the
+pipeline. Backward requires gradient propagation from downstream ranks, creating a real
+bubble where warmup activations sit in memory waiting. This difference -- typically a
+few GB -- can be decisive at the OOM boundary.
+
+```yaml
+actor:
+  archon:
+    pp_schedule: ZBVZeroBubble  # V-shape: less warmup memory than IZB
+```
+
+```{note}
+`ZBVZeroBubble` requires exactly 2 stages per rank (`stages_per_rank=2`).
+```
+
+### A.3 FSDP Parameter Resharding
+
+With PP enabled, FSDP defaults to keeping parameters unsharded after forward
+(`reshard_after_forward=False`) to avoid redundant all-gather communication per
+microbatch. This trades memory for speed -- each rank holds the full (unsharded)
+parameters of its assigned layers, adding ~`model_params_per_rank * (1 - 1/dp_shard)` in
+bf16.
+
+Override with `reshard_after_forward_policy: always` if communication overhead is
+acceptable:
+
+```yaml
+actor:
+  archon:
+    reshard_after_forward_policy: always  # reshard after each forward, saves memory
+```
+
+### A.4 Gradient Accumulation Overhead (FSDP + PP)
+
+This is an inherent cost of combining FSDP with PP and applies to **all** PP schedules
+(not just zero bubble).
+
+PyTorch's PP scheduler disables gradient synchronization
+(`set_requires_gradient_sync(False)`) and parameter resharding
+(`set_reshard_after_backward(False)`) for all backward microbatches except the last one.
+This means gradients accumulate in **unsharded fp32** form across microbatches rather
+than being reduce-scattered immediately.
+
+For a model with `P` parameters per rank, this adds up to `P * 4 bytes` (fp32) of
+gradient memory. For example, a 30B MoE model with PP=2 holds ~13.5B parameters per
+rank, resulting in ~54 GB of unsharded gradient buffers during the backward phase.
+
+This overhead **cannot be reduced by AReaL configuration alone** -- the only mitigation
+is to reduce parameters per rank via TP or EP.
+
+### A.5 When to Add TP/EP
+
+If OOM persists after tuning `n_mbs`, `reshard_after_forward_policy`, and activation
+checkpointing, the model likely exceeds the per-rank memory budget. Add tensor
+parallelism (`t2` or `t4`) or expert parallelism (`e2`, `e4`) to reduce parameters per
+rank. For MoE models, EP is preferred because expert weights typically dominate model
+size:
+
+```yaml
+# Before: archon:d2p2 (PP only, OOM)
+# After: archon:d1p2e2 (PP + EP, fits in memory)
+allocation_mode: sglang:d4+archon:d2p2e2
+```
+
+### A.6 Activation Checkpointing with PP
+
+Full AC (`gradient_checkpointing: true`) is strongly recommended with PP since the
+warmup phase holds activations from multiple forward passes simultaneously.
+
+For zero bubble schedules, the AC mode is further constrained:
+
+| AC mode                               | Zero bubble compatible | Notes                                       |
+| ------------------------------------- | ---------------------- | ------------------------------------------- |
+| `full`                                | Yes                    | Recommended for maximum memory savings      |
+| `selective` (layer-level, e.g. `"2"`) | Yes                    | Good balance of speed and memory            |
+| `selective` (`"op"`)                  | No                     | Per-op cache conflicts with split backward  |
+| `memory_budget`                       | No                     | Depends on torch.compile, which is disabled |
+
+### A.7 Memory Budget Rule of Thumb
+
+```{tip}
+Each rank needs memory for:
+1. Sharded model parameters: `model_size / (dp_shard * tp * ep)` in bf16
+2. Unsharded gradients during backward: `model_size / (tp * ep * pp)` in fp32
+3. Optimizer states: `2 * model_size / (dp_shard * tp * ep)` in fp32 (AdamW)
+4. Activations: ~`num_total_stages * (batch_tokens / n_mbs) * hidden_dim` in bf16
+
+If the sum exceeds GPU memory, increase TP, EP, or PP to reduce per-rank load.
+```
PATCH

echo "Patch applied successfully."
