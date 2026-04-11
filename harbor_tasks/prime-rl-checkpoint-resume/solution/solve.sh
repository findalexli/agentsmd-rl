#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (CheckpointManager class exists)
if grep -q 'class CheckpointManager:' src/zeroband/training/ckpt.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/README.md b/README.md
index a6d52794bb..7e41fe8ef3 100644
--- a/README.md
+++ b/README.md
@@ -130,7 +130,7 @@ CUDA_VISIBLE_DEVICES=1 uv run train @ configs/training/simple_math.toml

 *TBD*

-## Contributing
+## Developer

 *For now, development is only possible on CUDA-enabled devices. However, we build production-ready images for both CUDA (NVIDIA) and ROCM (AMD) GPUs that should work out of the box.*

@@ -142,7 +142,7 @@ CUDA_VISIBLE_DEVICES=1 uv run train @ configs/training/simple_math.toml
 uv run pre-commit install
 ```

-### Config System
+### Configs

 We use `pydantic-settings` to configure `prime-rl`. To get an overview of the available configurations, run the following command:

@@ -188,6 +188,59 @@ PRIME_MODEL__NAME=Qwen/Qwen3-4B uv run src/zeroband/inference/server.py @qwen8b.

 In this example, the CLI argument `--model.name Qwen/Qwen3-32B` will take precendence and the script will use `Qwen/Qwen3-32B` as the model name. If the CLI argument wasn't set, then the second config file would take precedence and the script would use `Qwen/Qwen-14B` as the model name. If the second config file wasn't set, then the first config file would take precedence and the script would use `Qwen/Qwen3-8B` as the model name. Finally, if the first config file wasn't set, then the environment variable would take precedence and the script would use `Qwen/Qwen-4B` as the model name. If the environment variable wasn't set, then the default value would be used and the script would use `Qwen/Qwen3-0.6B` as the model name.

+### Checkpointing
+
+Our codebase supports checkpointing. Because of the trainer/ orchestrator design, as well as the natural asynchrony checkpointing is non-standard.
+
+- Trainer (`src/zeroband/training/ckpt.py`): Checkpoints FSDP model shard, optimizer state and progress (training step, total samples, total tokens)
+- Orchestrator (`src/zeroband/training/ckpt.py`): Checkpoints orchestrator progress
+
+*NB: Each run with asynchrony level `async_level` and some checkpoint step `x`, requires weight checkpoints in the step range `[x-async_level, x]`. Currently we do not duplicate weight checkpoints into the `checkpoints` directory but simply keep them around in `weights`, by keeping the trainer from cleaning up weight checkpoints that are required for resuming training. This way, the orchestrator only needs to checkpoint its progress (read: step) to load the correct weights into the inference engine upon resuming.*
+
+The default checkpoint directory is `checkpoints` and each checkpoint step will live in a subdirectory enumerated by the step, i.e. `checkpoints/step_{step}`. The trainer checkpoint is called `trainer.pt` for single GPU workloads, else `trainer_{local_rank}.pt`. The orchestrator checkpoint is callec `orchestrator.pt`. Thus, this is a typical directory structure:
+
+```bash
+checkpoints
+├── step_10
+│   ├── orchestrator.pt
+│   └── trainer.pt
+├── step_25
+│   ├── orchestrator.pt
+│   └── trainer.pt
+└── step_30
+    ├── orchestrator.pt
+    └── trainer.pt
+```
+
+Checkpointing is configured by the `CheckpointConfig`, with the config key `--ckpt`. One can specify:
+- `--ckpt.path` to change the checkpoint directory (default: `checkpoints`)
+- `--ckpt.interval` to change the interval frequency (default: `50`)
+- `--ckpt.save-async` to save the checkpoint asynchronously (default: `False`)
+
+By default, runs do no write checkpoints to save disk space. To checkpoint every 10 steps on our debug RL run, run the following command
+
+```bash
+CUDA_VISIBLE_DEVICES=1 uv run train @ configs/training/reverse_text.toml --ckpt.interval 10
+```
+
+To resume a run use the `--ckpt.resume-step` flag. To resume from the checkpoint stpe 10 from the previous command, run the following command
+
+```bash
+CUDA_VISIBLE_DEVICES=1 uv run train @ configs/training/reverse_text.toml --ckpt.resume_step 10
+```
+
+Because we save progress information, resuming from a checkpoint is fully W&B compatible. By default, resuming from a checkpoint, will simply create a new run. To resume the same W&B run, you'd have to pass the same W&B run ID for both the trainer and the orchestrator, e.g.
+
+```bash
+CUDA_VISIBLE_DEVICES=1 uv run train @ configs/training/reverse_text.toml \
+  --monitor.wandb.project <project> \
+  --monitor.wandb.group <group> \
+  --ckpt.resume-step 10 \
+  --monitor.wandb.id <trainer-run-id> \
+  --orchestrator.monitor.wandb.id <orchestrator-run-id>
+```
+
+
 ### Tests

 Run the full test suite
PATCH

echo "Patch applied successfully."
