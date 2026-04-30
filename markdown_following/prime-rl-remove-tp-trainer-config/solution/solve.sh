#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency check: if ModelConfig no longer has tp field, patch is already applied
if ! grep -q 'tp:.*Annotated' src/prime_rl/configs/trainer.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b60fcc0732..c3f1027207 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -2,6 +2,7 @@

 Documenting changes which affect configuration usage patterns (added/moved/removed/renamed fields, notable logic changes).

+- **`model.tp` (trainer `ModelConfig`)**: Removed from the trainer model config. Existing trainer configs must delete this field; it is no longer accepted. (2026-03-26)
 - **`orchestrator.env[].num_workers`**: Added configurable env server worker count (`int | "auto"`, default: `"auto"`). When `"auto"`, scales based on concurrency (1 worker per 256 concurrent rollouts). Only used when the orchestrator spawns the env server (i.e. `address` is not set). (2026-03-25)
 - **`[model.vlm]` (NEW — replaces auto-detection)**: VLM mode is now opt-in via a `[model.vlm]` sub-config with required `vision_encoder_attr` and `language_model_attr` fields. There is no auto-detection — if you train a VLM, you must add `[model.vlm]`. Existing multimodal configs need the new section. See `docs/multimodal.md` for the table of known model attrs. (2026-03-24)
 - **`model.optimization_dtype` / `model.reduce_dtype` (VLM models, RL only)**: VLM dtype validation now only applies to RL training (`TrainerConfig`), not SFT. VLM models used with `sft` no longer require `optimization_dtype='bfloat16'` / `reduce_dtype='bfloat16'`. RL training still enforces both to match vLLM inference. (2026-03-24)
diff --git a/src/prime_rl/configs/rl.py b/src/prime_rl/configs/rl.py
index a66b376e90..5b2be55a3a 100644
--- a/src/prime_rl/configs/rl.py
+++ b/src/prime_rl/configs/rl.py
@@ -717,7 +717,7 @@ def auto_setup_router_replay(self):
     def auto_setup_deployment(self):
         if self.deployment.type == "single_node":  # single-node
             # set num_train_workers to the number of data replicas
-            non_data_parallel_size = self.trainer.model.cp * self.trainer.model.tp
+            non_data_parallel_size = self.trainer.model.cp
             if self.deployment.num_train_gpus > 1:
                 self.orchestrator.num_train_workers = self.deployment.num_train_gpus // non_data_parallel_size

diff --git a/src/prime_rl/configs/trainer.py b/src/prime_rl/configs/trainer.py
index 9c7d5ac6fb..ff63da0739 100644
--- a/src/prime_rl/configs/trainer.py
+++ b/src/prime_rl/configs/trainer.py
@@ -202,13 +202,6 @@ class ModelConfig(BaseModelConfig):
         ),
     ] = 1

-    tp: Annotated[
-        int,
-        Field(
-            description="The tensor parallelism size to use. If 1, then no TP will be used.",
-        ),
-    ] = 1
-
     cp: Annotated[
         int,
         Field(
diff --git a/src/prime_rl/trainer/parallel_dims.py b/src/prime_rl/trainer/parallel_dims.py
index dca275ea81..dbfe855723 100644
--- a/src/prime_rl/trainer/parallel_dims.py
+++ b/src/prime_rl/trainer/parallel_dims.py
@@ -37,7 +37,6 @@ class ParallelDims:
     dp_replicate: int
     dp_shard: int
     cp: int
-    tp: int
     pp: int
     ep: int
     world_size: int
@@ -50,25 +49,24 @@ def __post_init__(self):
         self._validate()

     def _validate(self):
-        dp_replicate, dp_shard, cp, tp, pp, ep = (
+        dp_replicate, dp_shard, cp, pp, ep = (
             self.dp_replicate,
             self.dp_shard,
             self.cp,
-            self.tp,
             self.pp,
             self.ep,
         )
-        for d in (dp_replicate, cp, tp, pp, ep):
+        for d in (dp_replicate, cp, pp, ep):
             assert d >= 1, "Parallelism degree should be >= 1, except for dp_shard"

         assert dp_shard == -1 or dp_shard >= 1, " dp_shard must -1 or >=1."
         if dp_shard < 0:
-            self.dp_shard = dp_shard = self.world_size // (dp_replicate * cp * tp * pp)
+            self.dp_shard = dp_shard = self.world_size // (dp_replicate * cp * pp)
         assert dp_shard >= 1

-        assert dp_replicate * dp_shard * cp * tp * pp == self.world_size, (
+        assert dp_replicate * dp_shard * cp * pp == self.world_size, (
             f"Invalid parallel dims: dp_replicate({dp_replicate}) * dp_shard({dp_shard}) * "
-            f"cp({cp}) * tp({tp}) * pp({pp}) != WORLD_SIZE({self.world_size})"
+            f"cp({cp}) * pp({pp}) != WORLD_SIZE({self.world_size})"
         )

         if ep > 1:
@@ -97,9 +95,8 @@ def _build_mesh_with_ep(self) -> DeviceMesh:
                 dp_shard_mod_ep,
                 dp_shard_in_ep,
                 self.cp,
-                self.tp,
             ],
-            ["pp", "dp_replicate", "dp_shard_mod_ep", "dp_shard_in_ep", "cp", "tp"],
+            ["pp", "dp_replicate", "dp_shard_mod_ep", "dp_shard_in_ep", "cp"],
         ):
             # dp_shard_mod_ep is needed even if it's 1, whose FSDP wrapping
             # helps the MoE layers do mixed precision training
@@ -158,8 +155,8 @@ def _build_mesh_without_ep(self) -> DeviceMesh:
         dims = []
         names = []
         for d, name in zip(
-            [self.pp, self.dp_replicate, self.dp_shard, self.cp, self.tp],
-            ["pp", "dp_replicate", "dp_shard", "cp", "tp"],
+            [self.pp, self.dp_replicate, self.dp_shard, self.cp],
+            ["pp", "dp_replicate", "dp_shard", "cp"],
         ):
             if d > 1 or name == "dp_shard":
                 dims.append(d)
@@ -245,10 +242,6 @@ def dp_cp_enabled(self):
     def fsdp_enabled(self):
         return self.dp_shard_enabled or self.cp_enabled

-    @property
-    def tp_enabled(self):
-        return self.tp > 1
-
     @property
     def pp_enabled(self):
         return self.pp > 1
@@ -263,17 +256,14 @@ def fsdp_gradient_divide_factor(self) -> int:

     @cached_property
     def non_data_parallel_size(self):
-        return self.cp * self.tp * self.pp
+        return self.cp * self.pp

     @cached_property
     def seq_len_divisor(self):
-        # Sequence Parallel requires that seq_len be divisible by TP degree.
-        # https://github.com/pytorch/torchtitan/pull/640#discussion_r1849481001
-
         # Context Parallel requires that seq_len be divisible by 2 * CP degree,
         # when load balancing is enabled (by default).
         # https://github.com/pytorch/pytorch/blob/4f62dcc/torch/distributed/tensor/experimental/_attention.py#L1246
-        return self.tp * (self.cp * 2)
+        return self.cp * 2

     @cached_property
     def logger(self):
@@ -286,7 +276,6 @@ def get_parallel_dims(config: ModelConfig, seq_len: int | None = None) -> Parall
         dp_replicate=config.dp_replicate,
         dp_shard=-1,
         cp=config.cp,
-        tp=config.tp,
         pp=1,
         ep=config.ep,
         world_size=dist.get_world_size(),
@@ -297,8 +286,7 @@ def get_parallel_dims(config: ModelConfig, seq_len: int | None = None) -> Parall
         raise ValueError(
             f"Sequence length ({seq_len}) must be divisible by "
             f"seq_len_divisor ({parallel_dims.seq_len_divisor}) for the given parallel dimensions. "
-            f"This requirement comes from context parallel (CP={config.cp}) and "
-            f"tensor parallel (TP={config.tp}) configurations."
+            f"This requirement comes from context parallel (CP={config.cp})."
         )

     return parallel_dims
diff --git a/src/prime_rl/trainer/sft/train.py b/src/prime_rl/trainer/sft/train.py
index dbbdeb290b..67e27b74b9 100644
--- a/src/prime_rl/trainer/sft/train.py
+++ b/src/prime_rl/trainer/sft/train.py
@@ -89,10 +89,10 @@ def train(config: SFTConfig):
     # Initialize parallel dimensions
     parallel_dims = get_parallel_dims(config.model, config.data.seq_len)

-    total_micro_batches = config.data.batch_size * config.model.cp * config.model.tp
+    total_micro_batches = config.data.batch_size * config.model.cp
     micro_batches_per_step = world.world_size * config.data.micro_batch_size
     assert total_micro_batches % micro_batches_per_step == 0, (
-        f"batch_size * cp * tp ({total_micro_batches}) must be divisible by "
+        f"batch_size * cp ({total_micro_batches}) must be divisible by "
         f"world_size * micro_batch_size ({micro_batches_per_step})"
     )
     grad_accum_steps = total_micro_batches // micro_batches_per_step
@@ -152,7 +152,7 @@ def train(config: SFTConfig):

     # Set up the dataset and dataloader
     logger.info(f"Initializing data ({config.data})")
-    dataset = setup_dataset(tokenizer, config.data, config.model.cp * config.model.tp)
+    dataset = setup_dataset(tokenizer, config.data, config.model.cp)
     dataloader = setup_dataloader(dataset, config.data)
     dataiter = iter(dataloader)

@@ -258,7 +258,7 @@ def run_eval_loop(data_iter):

     def run_validation(step: int) -> None:
         val_dataset = setup_dataset(
-            tokenizer, config.val.data, config.model.cp * config.model.tp, max_epochs=1, raw_dataset=val_raw_dataset
+            tokenizer, config.val.data, config.model.cp, max_epochs=1, raw_dataset=val_raw_dataset
         )
         val_dataloader = setup_dataloader(val_dataset, config.val.data)

@@ -410,8 +410,8 @@ def run_validation(step: int) -> None:
             memory_profiler.step()

         # Compute step metrics
-        # Divide by CP and TP since those ranks process the same data
-        num_tokens = config.data.batch_size * config.data.seq_len // (config.model.cp * config.model.tp)
+        # Divide by CP since those ranks process the same data
+        num_tokens = config.data.batch_size * config.data.seq_len // config.model.cp
         progress.total_tokens += num_tokens
         progress.total_samples = dataset.step
         perf_counter = get_perf_counter(model, config.data.seq_len)

PATCH

echo "Patch applied successfully."
