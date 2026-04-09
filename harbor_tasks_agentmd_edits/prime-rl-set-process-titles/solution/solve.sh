#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'setproctitle' pyproject.toml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/pyproject.toml b/pyproject.toml
index a2215844dd..a5e7ed01ab 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -28,6 +28,7 @@ dependencies = [
     "tenacity>=8.2.0",
     "openai>=1.106.1",
     "rich>=14.0.0",
+    "setproctitle>=1.3.0",
     "uvloop>=0.21.0",
     "torchtitan",
     "verifiers",
@@ -114,7 +115,7 @@ override-dependencies = [

 [tool.uv.sources]
 torch = { index = "pytorch-cu128" }
-verifiers = { git = "https://github.com/PrimeIntellect-ai/verifiers.git", rev = "5d75d97" }
+verifiers = { git = "https://github.com/PrimeIntellect-ai/verifiers.git", rev = "adf8138" }
 torchtitan = { git = "https://github.com/pytorch/torchtitan", rev = "a1fdd7e" }
 dion = { git = "https://github.com/samsja/dion.git", rev = "d891eeb" }
 transformers = { git = "https://github.com/huggingface/transformers.git", rev = "5c1c72b" }
diff --git a/skills/monitor-run/SKILL.md b/skills/monitor-run/SKILL.md
index 32ae87f06c..6ef16b4674 100644
--- a/skills/monitor-run/SKILL.md
+++ b/skills/monitor-run/SKILL.md
@@ -83,6 +83,57 @@ Log paths are consistent across deployment types — `logs/trainer.log` and `log
     └── ...
 ```

+### Identify processes via process tree
+
+All prime-rl and verifiers processes set custom process titles using `setproctitle`, making them easy to identify in `ps`, `htop`, and `pstree`.
+
+#### Process titles
+
+| Process | Title |
+|---------|-------|
+| RL launcher (`uv run rl`) | `PRIME-RL::Launcher` |
+| SFT launcher (`uv run sft`) | `PRIME-RL::SFT` |
+| Inference server (`uv run inference`) | `PRIME-RL::Inference` |
+| Orchestrator (`uv run orchestrator`) | `PRIME-RL::Orchestrator` |
+| RL trainer (via torchrun) | `PRIME-RL::Trainer` |
+| SFT trainer (via torchrun) | `PRIME-RL::SFTTrainer` |
+| Env server (`uv run env-server`) | `PRIME-RL::EnvServer` |
+| vLLM engine core (spawned by inference) | `VLLM::EngineCore` |
+| Env server (spawned by orchestrator) | `Verifiers::EnvServer` |
+| Env worker N | `Verifiers::EnvWorker{N}` |
+
+#### Inspecting the process tree
+
+```bash
+# Find all prime-rl / verifiers processes
+ps -eo pid,comm,args | grep -E "PRIME-RL|Verifiers"
+
+# Show the full tree from the launcher PID (filter threads with grep -v)
pstree -ap <launcher_pid> | grep -v '{.*}'
+
+# Find vLLM processes specifically (engine core, router)
+ps -eo pid,comm,args | grep -E "VLLM::"
+
+# Find vLLM processes on GPUs
+nvidia-smi --query-compute-apps=pid,name,gpu_uuid --format=csv,noheader
+```
+
+A typical single-node RL run process tree:
+
+```
+PRIME-RL::Launcher
+├── PRIME-RL::Inference          (vLLM server, GPU 0)
+├── PRIME-RL::Orchestrator       (CPU-only, data/scheduling)
+│   ├── Verifiers::EnvServer     (ZMQ env server per environment)
+│   │   ├── Verifiers::EnvWorker0
+│   │   ├── Verifiers::EnvWorker1
+│   │   └── ...
+│   └── ...
+├── torchrun
+│   └── PRIME-RL::Trainer        (RL trainer, GPU 1+)
+└── tail -F trainer.log
+```
+
 ### Check performance

 #### Trainer
diff --git a/src/prime_rl/entrypoints/inference.py b/src/prime_rl/entrypoints/inference.py
index 50f267dc80..cae9bf3334 100644
--- a/src/prime_rl/entrypoints/inference.py
+++ b/src/prime_rl/entrypoints/inference.py
@@ -8,6 +8,7 @@
 from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import format_log_message, get_config_dir, get_log_dir
+from prime_rl.utils.process import set_proc_title

 INFERENCE_TOML = "inference.toml"
 INFERENCE_SBATCH = "inference.sbatch"
@@ -137,6 +138,7 @@ def inference(config: InferenceConfig):


 def main():
+    set_proc_title("Inference")
     inference(cli(InferenceConfig))


diff --git a/src/prime_rl/entrypoints/rl.py b/src/prime_rl/entrypoints/rl.py
index 7ed60e9ceb..071e45a16f 100644
--- a/src/prime_rl/entrypoints/rl.py
+++ b/src/prime_rl/entrypoints/rl.py
@@ -15,7 +15,7 @@
 from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import format_log_message, validate_output_dir
-from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process
+from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process, set_proc_title
 from prime_rl.utils.utils import (
     get_free_port,
     get_log_dir,
@@ -171,7 +171,7 @@ def rl_local(config: RLConfig):
     try:
         # Optionally, start inference process
         if config.inference:
-            inference_cmd = ["uv", "run", "inference", "@", (config_dir / INFERENCE_TOML).as_posix()]
+            inference_cmd = ["inference", "@", (config_dir / INFERENCE_TOML).as_posix()]
             logger.info(f"Starting inference on GPU(s) {' '.join(map(str, infer_gpu_ids))}")
             logger.debug(f"Inference start command: {' '.join(inference_cmd)}")
             # If we don't log stdout, the server hangs
@@ -216,7 +216,7 @@ def rl_local(config: RLConfig):
                     "or omit teacher_inference and configure orchestrator.teacher_model to use an existing server."
                 )

-            teacher_inference_cmd = ["uv", "run", "inference", "@", (config_dir / TEACHER_INFERENCE_TOML).as_posix()]
+            teacher_inference_cmd = ["inference", "@", (config_dir / TEACHER_INFERENCE_TOML).as_posix()]
             logger.info(f"Starting teacher inference process on GPU(s) {' '.join(map(str, teacher_gpu_ids))}")
             logger.debug(f"Teacher inference start command: {' '.join(teacher_inference_cmd)}")
             with open(log_dir / "teacher_inference.log", "w") as log_file:
@@ -251,8 +251,6 @@ def rl_local(config: RLConfig):

         # Start orchestrator process
         orchestrator_cmd = [
-            "uv",
-            "run",
             "orchestrator",
             "@",
             (config_dir / ORCHESTRATOR_TOML).as_posix(),
@@ -288,11 +286,6 @@ def rl_local(config: RLConfig):

         # Start training process
         trainer_cmd = [
-            "uv",
-            "run",
-            "env",
-            "PYTHONUNBUFFERED=1",
-            "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
             "torchrun",
             f"--rdzv-endpoint=localhost:{get_free_port()}",
             f"--rdzv-id={uuid.uuid4().hex}",
@@ -317,6 +310,7 @@ def rl_local(config: RLConfig):
                     **wandb_shared_env,
                     "WANDB_SHARED_LABEL": "trainer",
                     "CUDA_VISIBLE_DEVICES": ",".join(map(str, trainer_gpu_ids)),
+                    "PYTHONUNBUFFERED": "1",
                     "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
                     "LOGURU_FORCE_COLORS": "1",
                     "WANDB_PROGRAM": "uv run rl",
@@ -535,6 +529,7 @@ def rl(config: RLConfig):


 def main():
+    set_proc_title("Launcher")
     rl(cli(RLConfig))


diff --git a/src/prime_rl/entrypoints/sft.py b/src/prime_rl/entrypoints/sft.py
index 0e100a631e..df79803458 100644
--- a/src/prime_rl/entrypoints/sft.py
+++ b/src/prime_rl/entrypoints/sft.py
@@ -12,7 +12,7 @@
 from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import format_log_message, get_config_dir, get_log_dir, validate_output_dir
-from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process
+from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process, set_proc_title
 from prime_rl.utils.utils import get_free_port

 SFT_TOML = "sft.toml"
@@ -114,11 +114,6 @@ def sft_local(config: SFTConfig):
     log_dir.mkdir(parents=True, exist_ok=True)

     trainer_cmd = [
-        "uv",
-        "run",
-        "env",
-        "PYTHONUNBUFFERED=1",
-        "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
         "torchrun",
         f"--rdzv-endpoint=localhost:{get_free_port()}",
         f"--rdzv-id={uuid.uuid4().hex}",
@@ -146,6 +141,7 @@ def sft_local(config: SFTConfig):
                 trainer_cmd,
                 env={
                     **os.environ,
+                    "PYTHONUNBUFFERED": "1",
                     "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
                 },
                 stdout=log_file,
@@ -203,6 +199,7 @@ def sft(config: SFTConfig):


 def main():
+    set_proc_title("SFT")
     sft(cli(SFTConfig))


diff --git a/src/prime_rl/orchestrator/env_server/env_server.py b/src/prime_rl/orchestrator/env_server/env_server.py
index 17634aacc5..64e67b783a 100644
--- a/src/prime_rl/orchestrator/env_server/env_server.py
+++ b/src/prime_rl/orchestrator/env_server/env_server.py
@@ -6,6 +6,7 @@
 from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import get_log_dir
+from prime_rl.utils.process import set_proc_title
 from prime_rl.utils.utils import clean_exit, get_env_ids_to_install, install_env, strip_env_version


@@ -36,6 +37,7 @@ def run_server(config: EnvServerConfig):

 def main():
     """Main entry-point for env-server. Run using `uv run env-server`"""
+    set_proc_title("EnvServer")
     run_server(cli(EnvServerConfig))


diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index 537761c452..5acc74ad4a 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.md
@@ -66,6 +66,7 @@
 from prime_rl.utils.heartbeat import Heartbeat
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.monitor import setup_monitor
+from prime_rl.utils.process import set_proc_title
 from prime_rl.utils.temp_scheduling import compute_temperature
 from prime_rl.utils.utils import (
     clean_exit,
@@ -916,7 +917,7 @@ def compute_solve_rates(df):

 def main():
     """Main entry-point for orchestrator. Run using `uv run orchestrator`"""
-
+    set_proc_title("Orchestrator")
     asyncio.run(orchestrate(cli(OrchestratorConfig)))


diff --git a/src/prime_rl/trainer/rl/train.py b/src/prime_rl/trainer/rl/train.py
index ed17bb10a2..280a5306dd 100644
--- a/src/prime_rl/trainer/rl/train.py
+++ b/src/prime_rl/trainer/rl/train.py
@@ -58,6 +58,7 @@
 from prime_rl.utils.metrics_server import HealthServer, MetricsServer, RunStats
 from prime_rl.utils.monitor import setup_monitor
 from prime_rl.utils.config import cli
+from prime_rl.utils.process import set_proc_title
 from prime_rl.utils.utils import clean_exit, resolve_latest_ckpt_step, to_col_format
 from ring_flash_attn import substitute_hf_flash_attn
 from torchtitan.distributed.utils import clip_grad_norm_
@@ -647,7 +648,7 @@ def load_run_checkpoint(_optimizer, idx: int) -> None:

 def main():
     """Main entry-point for RL trainer. Run using `uv run trainer`"""
-
+    set_proc_title("Trainer")
     train(cli(TrainerConfig))


diff --git a/src/prime_rl/trainer/sft/train.py b/src/prime_rl/trainer/sft/train.py
index 5a870ad891..f48e30bcec 100644
--- a/src/prime_rl/trainer/sft/train.py
+++ b/src/prime_rl/trainer/sft/train.py
@@ -45,6 +45,7 @@
 from prime_rl.utils.heartbeat import Heartbeat
 from prime_rl.utils.monitor import setup_monitor
 from prime_rl.utils.config import cli
+from prime_rl.utils.process import set_proc_title
 from prime_rl.utils.utils import clean_exit, to_col_format
 import torch.distributed as dist
 from liger_kernel.transformers.cross_entropy import LigerCrossEntropyLoss
@@ -538,6 +539,7 @@ def run_validation(step: int) -> None:


 def main():
+    set_proc_title("SFTTrainer")
     train(cli(SFTConfig))


diff --git a/src/prime_rl/utils/process.py b/src/prime_rl/utils/process.py
index 1e5a034c77..c1d569a70e 100644
--- a/src/prime_rl/utils/process.py
+++ b/src/prime_rl/utils/process.py
@@ -2,6 +2,21 @@
 from subprocess import Popen

+import setproctitle
+
+PRIME_RL_PROC_PREFIX = "PRIME-RL"
+
+
+def set_proc_title(name: str) -> None:
+    """Set the process title for visibility in tools like ``ps`` and ``htop``.
+
+    Args:
+        name: A short, descriptive label (e.g. ``Trainer``, ``Orchestrator``).
+              The process title is set to ``{PRIME_RL_PROC_PREFIX}::{name}``.
+    """
+    title = f"{PRIME_RL_PROC_PREFIX}::{name}"
+    setproctitle.setproctitle(title)
+

 def cleanup_threads(threads: list[Thread]):
     """Cleanup a list of threads"""

PATCH

echo "Patch applied successfully."
