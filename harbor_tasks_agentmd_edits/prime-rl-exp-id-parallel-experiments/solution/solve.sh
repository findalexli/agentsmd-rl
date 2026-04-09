#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'exp_id.*experiment ID' src/prime_rl/rl.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the embedded diff
cat << 'PATCHOF' | git apply - --whitespace=fix
diff --git a/README.md b/README.md
index 3f62e642e5..0362cee476 100644
--- a/README.md
+++ b/README.md
@@ -92,9 +92,7 @@ uv run rl \
 </details>
 
 
-## Entrypoints
-
-### Setup
+## Additional Setup
 
 1. If you want to log your runs to W&B (`wandb`), log in
 
@@ -116,9 +114,19 @@ uv run huggingface-cli login
 ulimit -n 32000
 ```
 
-### RL
+4.  We provide a convenient tmux layout script to start a run and view logs. To start the session simply run
+
+```bash
+./tmux.sh
+```
+
+Then, paste the experiment entrypoints detailed below in the `Trainer` pane to start your run!
+
+## RL
+
+### Single Node Training
 
-We provide a convenience endpoint `rl` for single-node RL experiments. It configures and starts the trainer, orchestrator and, optionally, an inference server. It enforces correctly setting shared configs (e.g. the model name or async level should be the same across all modules) and dispatches and monitors subprocesses. To stream the logs from each module, we use file logging, by default only the trainer logs will be displayed on the main process. 
+We provide a convenience endpoint `rl` for single-node RL experiments. It configures and starts the trainer, orchestrator and, optionally, an inference server. It enforces correctly setting shared configs (e.g. the model name or async level should be the same across all modules) and dispatches and monitors subprocesses. To stream the logs from each module we use file logging. By default, only the trainer logs will be displayed on the main process (*use the tmux layout script to conveniently view all logs*).
 
 To check all available configuration options, run `uv run rl --help`.
 
@@ -146,9 +154,11 @@ uv run rl \
   --trainer @ configs/trainer/hendrycks_math/1b.toml \
   --orchestrator @ configs/orchestrator/hendrycks_math/1b.toml \
   --inference @ configs/inference/hendrycks_math/1b.toml \
-  --inference.parallel.dp 1
+  --trainer-gpus 2 --inference-gpus 6
 ```
 
+*NB: This setup requires 8 GPUs - 2 are used for the FSDP trainer, 6 are used for inference.*
+
 **INTELLECT-2 Math**
 
 Train a small model (`willcb/DeepSeek-R1-Distill-Qwen-1.5B`) on complex math questions from the INTELLECT-2 dataset.
@@ -161,59 +171,49 @@ uv run rl \
   --trainer-gpus 2 --inference-gpus 6
 ```
 
-*NB: This setup requires 8 GPUs - 2 are used for the FSDP trainer, 6 are used for inference with TP=2 and DP=3.*
+*NB: This setup requires 8 GPUs - 2 are used for the FSDP trainer, 6 are used for inference.*
 
+### Multi-Node Training
 
-### Tmux Layout
+*TBD*
 
-We provide a convenient tmux layout script to start a run and view all the logs at the same time. The recommended workflow is:
+### Multiple Experiments per Node
 
-1. Start a pre-layouted tmux session using the tmux script
+For small models/ quick ablations, it can be more efficient to parallelize experiments within a node (e.g. split your GPUs to run two experiments in parallel). Because the trainer communicates with the orchestrator via a shared file system, and the orchestrator communicates with the inference engine via an OAI-compatible API, the connection points have to be uniquely set. For example, if you have access to 4 GPUs you can run two 2 GPU training runs in parallel as follows:
+
+Start the first experiment as normal, but specify a unique experiment identifier (*will use the first 2 GPUs*)
 
 ```bash
-./tmux.sh
+./tmux.sh exp-1
 ```
 
-2. Start the trainer and orchestrator in the `Trainer` pane.
-
 ```bash
+# Start the first experiment
 uv run rl \
   --trainer @ configs/trainer/reverse_text.toml \
   --orchestrator @ configs/orchestrator/reverse_text.toml \
-  --inference @ configs/inference/reverse_text.toml
-```
-
-#### Standalone Inference Server
-You can optionally start the inference server individually to avoid the long vllm warmup at each run restart. Useful for development.
-
-1. Start the pre-layouted tmux session using the tmux script
-
-```bash
-./tmux.sh
+  --inference @ configs/inference/reverse_text.toml \
+  --exp-id exp-1
 ```
 
-2. Start the inference server in the `Inference` pane.
+For the second experiment, configure a new server port for the inference engine and orchestrator and choose a new experiment identifier (*will use the first 2 GPUs*)
 
 ```bash
-uv run inference @ configs/inference/reverse_text.toml
+./tmux.sh exp-2
 ```
 
-3. You can now start the trainer and orchestrator in the `Trainer` pane.
-
 ```bash
-uv run rl \
+# Start the second experiment
+CUDA_VISIBLE_DEVICES=3,4 uv run rl \
   --trainer @ configs/trainer/reverse_text.toml \
-  --orchestrator @ configs/orchestrator/reverse_text.toml
-```
-
-To kill the tmux session when you're done:
-
-```bash
-./tmux.sh kill
+  --orchestrator @ configs/orchestrator/reverse_text.toml \
+  --inference @ configs/inference/reverse_text.toml \
+  --inference.server.port 8001 \
+  --orchestrator.client.port 8001 \
+  --exp-id exp-2
 ```
 
-
-### Evals
+## Evals
 
 We provide a convenience endpoint for running a full evaluation suite of common benchmarks such as AIME, MATH-500 or LiveCodeBench against your model using the `eval` entrypoint.
 
@@ -276,6 +276,36 @@ PRIME_MODEL__NAME=Qwen/Qwen3-4B uv run inference @qwen8b.toml @qwen14b.toml --mo
 
 In this example, the CLI argument `--model.name Qwen/Qwen3-32B` will take precendence and the script will use `Qwen/Qwen3-32B` as the model name. If the CLI argument wasn't set, then the second config file would take precedence and the script would use `Qwen/Qwen-14B` as the model name. If the second config file wasn't set, then the first config file would take precedence and the script would use `Qwen/Qwen3-8B` as the model name. Finally, if the first config file wasn't set, then the environment variable would take precedence and the script would use `Qwen/Qwen-4B` as the model name. If the environment variable wasn't set, then the default value would be used and the script would use `Qwen/Qwen3-0.6B` as the model name.
 
+### Persistent Inference Server
+
+For development purposes it is useful start the inference server once and keep it alive across experiments to avoid suffering the vLLM startup time repeatedly. The recommended workflow is as follows:
+
+1. Start the pre-layouted tmux session using the tmux script
+
+```bash
+./tmux.sh
+```
+
+2. Start the inference server in the `Inference` pane.
+
+```bash
+uv run inference @ configs/inference/reverse_text.toml
+```
+
+3. Start the trainer and orchestrator in the `Trainer` pane.
+
+```bash
+uv run rl \
+  --trainer @ configs/trainer/reverse_text.toml \
+  --orchestrator @ configs/orchestrator/reverse_text.toml
+```
+
+To kill the tmux session when you're done:
+
+```bash
+./tmux.sh kill
+```
+
 ### Checkpointing
 
 Our codebase supports checkpointing. Because of the trainer/ orchestrator design, as well as the natural asynchrony checkpointing is non-standard.
@@ -361,8 +391,7 @@ Often it will be most convenient to benchmark the full RL run. This will automat
 uv run rl   \
   --trainer @ configs/trainer/reverse_text.toml  \
   --orchestrator @ configs/orchestrator/reverse_text.toml \
-  --inference @ configs/inference/reverse_text.toml \
-  --bench
+  --inference @ configs/inference/reverse_text.toml
 ```
 
 ### Tests
diff --git a/src/prime_rl/eval/eval.py b/src/prime_rl/eval/eval.py
index 4b8d4998c8..ba0ede32aa 100644
--- a/src/prime_rl/eval/eval.py
+++ b/src/prime_rl/eval/eval.py
@@ -28,7 +28,7 @@ async def eval(config: EvalConfig):
     monitor = setup_monitor(config.monitor, None, run_config=config)
 
     # Setup client
-    logger.info(f"Initializing OpenAI client ({config.client.base_url})")
+    logger.info(f"Initializing OpenAI client ({config.client.host}:{config.client.port})")
     client = setup_client(config.client)
 
     # Check health of the client
diff --git a/src/prime_rl/orchestrator/client.py b/src/prime_rl/orchestrator/client.py
index b6aedada69..2f3b09f3d2 100644
--- a/src/prime_rl/orchestrator/client.py
+++ b/src/prime_rl/orchestrator/client.py
@@ -21,8 +21,9 @@ def setup_client(client_config: ClientConfig) -> AsyncOpenAI:
         max_keepalive_connections=28000,  # OAI default: 100
     )
     http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
+    base_url = f"http://{client_config.host}:{client_config.port}/v1"
     return AsyncOpenAI(
-        base_url=client_config.base_url,
+        base_url=base_url,
         api_key=client_config.api_key,
         max_retries=10,  # OAI default: 2 (does exponential backoff and reasonable timeout in between retries)
         http_client=http_client,
diff --git a/src/prime_rl/orchestrator/config.py b/src/prime_rl/orchestrator/config.py
index 847cb9e701..d0b19a8e64 100644
--- a/src/prime_rl/orchestrator/config.py
+++ b/src/prime_rl/orchestrator/config.py
@@ -11,12 +11,19 @@
 class ClientConfig(BaseConfig):
     """Configures the client to be used for inference."""
 
-    base_url: Annotated[
+    host: Annotated[
         str,
         Field(
-            description="Base URL of the OpenAI API. By default, it is set to a local inference server.",
+            description="Host to use for the OpenAI API. By default, it is set to a local inference server.",
         ),
-    ] = "http://localhost:8000/v1"
+    ] = "localhost"
+
+    port: Annotated[
+        int,
+        Field(
+            description="Port to use for the OpenAI API. By default, it is set to a local inference server.",
+        ),
+    ] = 8000
 
     api_key: Annotated[
         str,
diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index cd6fc3ac58..3f7bc46ac3 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.py
@@ -50,7 +50,7 @@ async def orchestrate(config: OrchestratorConfig):
         )
 
     # Setup client
-    logger.info(f"Initializing OpenAI client ({config.client.base_url})")
+    logger.info(f"Initializing OpenAI client ({config.client.host}:{config.client.port})")
     client = setup_client(config.client)
 
     # Load tokenizer
diff --git a/src/prime_rl/rl.py b/src/prime_rl/rl.py
index 9e54e974ba..c2da8e5741 100644
--- a/src/prime_rl/rl.py
+++ b/src/prime_rl/rl.py
@@ -22,6 +22,7 @@
 from prime_rl.utils.config import WandbMonitorConfig
 from prime_rl.utils.logger import format_message, format_time, get_logger, set_logger, setup_handlers
 from prime_rl.utils.pydantic_config import BaseSettings, get_temp_toml_file, parse_argv
+from prime_rl.utils.utils import get_cuda_visible_devices, get_free_port
 
 
 class LogConfig(BaseSettings):
@@ -53,7 +54,10 @@ class RLConfig(BaseSettings):
 
     log: LogConfig = LogConfig()
 
+    exp_id: Annotated[str | None, Field(description="The experiment ID. If set, will be used to identify shared resources, like log files, weight and rollout directories, etc.")] = "rl" # This value has to match the `DEFAULT_EXPERIMENT_ID` in `tmux.sh`
+
     trainer_gpus: Annotated[int, Field(description="The number of GPUs to use for trainer.")] = 1
+
     inference_gpus: Annotated[int, Field(description="The number of GPUs to use for inference.")] = 1
 
     bench: Annotated[
@@ -149,6 +153,15 @@ def auto_setup_async_level(self):
         self.orchestrator.async_level = self.trainer.async_level
         return self
 
+    @model_validator(mode="after")
+    def auto_setup_exp(self):
+        if self.exp_id:
+            self.log.path = self.log.path / self.exp_id
+            self.trainer.data.path = self.trainer.data.path / self.exp_id
+            self.trainer.weights.path = self.trainer.weights.path / self.exp_id
+            # Note: Will be shared to orchestrator via `auto_setup_paths`
+        return self
+
     @model_validator(mode="after")
     def auto_setup_paths(self):
         # Ensure trainer and orchestrator use the same paths for communicating data and weights
@@ -269,7 +282,9 @@ def rl(config: RLConfig):
     monitor_threads: list[Thread] = []
     error_queue: list[Exception] = []
     stop_events: dict[str, Event] = {}
-    all_gpus = list(range(config.trainer_gpus + config.inference_gpus))
+    all_devices = get_cuda_visible_devices()
+    devices = all_devices[: config.trainer_gpus + config.inference_gpus]
+    logger.info(f"Available GPUs: {', '.join(map(str, all_devices))} (using: {', '.join(map(str, devices))})")
 
     try:
         # Optionally, start inference process
@@ -279,8 +294,8 @@ def rl(config: RLConfig):
                 tomli_w.dump(config.inference.model_dump(exclude_none=True, mode="json"), f)
 
             inference_cmd = ["uv", "run", "inference", "@", inference_file.as_posix()]
-            inference_gpu_ids = all_gpus[: config.inference_gpus]
-            logger.info(f"Starting inference process on GPUs {' '.join(map(str, inference_gpu_ids))}")
+            inference_gpu_ids = devices[: config.inference_gpus]
+            logger.info(f"Starting inference process on GPU(s) {' '.join(map(str, inference_gpu_ids))}")
             logger.debug(f"Inference start command: {' '.join(inference_cmd)}")
             # If we don't log stdout, the server hangs
             with open(config.log.path / "inference.log", "w") as log_file:
@@ -353,14 +368,16 @@ def rl(config: RLConfig):
             "uv",
             "run",
             "torchrun",
+            f"--rdzv-endpoint=localhost:{get_free_port()}",
+            f"--rdzv-id={config.exp_id}",
             "--nproc-per-node",
             str(config.trainer_gpus),
             "src/prime_rl/trainer/train.py",
             "@",
             trainer_file.as_posix(),
         ]
-        train_gpu_ids = all_gpus[config.inference_gpus :]
-        logger.info(f"Starting trainer process on GPUs {' '.join(map(str, train_gpu_ids))}")
+        train_gpu_ids = devices[config.inference_gpus :]
+        logger.info(f"Starting trainer process on GPU(s) {' '.join(map(str, train_gpu_ids))}")
         logger.debug(f"Training start command: {' '.join(trainer_cmd)}")
         with open(config.log.path / "trainer.log", "w") as log_file:
             trainer_process = Popen(
diff --git a/src/prime_rl/utils/utils.py b/src/prime_rl/utils/utils.py
index efb0fb3d5a..758ec7e696 100644
--- a/src/prime_rl/utils/utils.py
+++ b/src/prime_rl/utils/utils.py
@@ -1,9 +1,11 @@
 import functools
+import os
 import time
 from collections import defaultdict
 from pathlib import Path
 from typing import Any
 
+import torch
 import torch.distributed as dist
 import wandb
 
@@ -217,3 +219,21 @@ def get_step_path(path: Path, step: int) -> Path:
 
 def get_weight_ckpt_model_path(weight_dir: Path, step: int) -> Path:
     return weight_dir / f"step_{step}" / "pytorch_model.bin"
+
+def get_free_port() -> int:
+    """Find and return a free port"""
+    import socket
+    
+    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
+        s.bind(('', 0))  # Bind to any available port
+        s.listen(1)
+        port = s.getsockname()[1]
+    return port
+
+def get_cuda_visible_devices() -> list[int]:
+    """Returns the list of availble CUDA devices, taking into account the CUDA_VISIBLE_DEVICES environment variable."""
+    cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES")
+    if cuda_visible is None:
+        # Default to all devices if the environment variable is not set
+        return list(range(torch.cuda.device_count()))
+    return list(sorted([int(device) for device in cuda_visible.split(",")]))
\ No newline at end of file
diff --git a/tmux.sh b/tmux.sh
index b3215a9fa8..cd7f192b10 100755
--- a/tmux.sh
+++ b/tmux.sh
@@ -1,16 +1,35 @@
 #!/bin/bash
 
-# Session name
-SESSION_NAME="rl"
+# Default session name
+DEFAULT_EXPERIMENT_ID="rl"
 
-# Check for kill argument
-if [ "$1" = "kill" ]; then
-    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
-        echo "Killing tmux session: $SESSION_NAME"
-        tmux kill-session -t "$SESSION_NAME"
-        echo "Session '$SESSION_NAME' terminated."
+# Parse arguments
+EXPERIMENT_NAME="$DEFAULT_EXPERIMENT_ID"
+KILL_SESSION=false
+
+# Parse command line arguments
+while [[ $# -gt 0 ]]; do
+    case $1 in
+        kill)
+            KILL_SESSION=true
+            shift
+            ;;
+        *)
+            # If it's not 'kill', treat it as session name
+            EXPERIMENT_NAME="$1"
+            shift
+            ;;
+    esac
+done
+
+# Handle kill command
+if [ "$KILL_SESSION" = true ]; then
+    if tmux has-session -t "$EXPERIMENT_NAME" 2>/dev/null; then
+        echo "Killing tmux session: $EXPERIMENT_NAME"
+        tmux kill-session -t "$EXPERIMENT_NAME"
+        echo "Session '$EXPERIMENT_NAME' terminated."
     else
-        echo "Session '$SESSION_NAME' not found."
+        echo "Session '$EXPERIMENT_NAME' not found."
     fi
     exit 0
 fi
@@ -18,141 +37,141 @@ fi
 # Check if we're already inside a tmux session
 if [ -n "$TMUX" ]; then
     # We're inside tmux, so switch to the session instead of attaching
-    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
-        echo "Session '$SESSION_NAME' already exists. Switching..."
-        tmux switch-client -t "$SESSION_NAME"
+    if tmux has-session -t "$EXPERIMENT_NAME" 2>/dev/null; then
+        echo "Session '$EXPERIMENT_NAME' already exists. Switching..."
+        tmux switch-client -t "$EXPERIMENT_NAME"
     else
-        echo "Creating new tmux session: $SESSION_NAME"
-        tmux new-session -d -s "$SESSION_NAME" -n "RL"
+        echo "Creating new tmux session: $EXPERIMENT_NAME"
+        tmux new-session -d -s "$EXPERIMENT_NAME" -n "RL"
         
         # Window 1: RL - Create the layout first
         # Create 2 more panes for a total of 3
-        tmux split-window -v -t "$SESSION_NAME:RL.0"
-        tmux split-window -v -t "$SESSION_NAME:RL.1"
+        tmux split-window -v -t "$EXPERIMENT_NAME:RL.0"
+        tmux split-window -v -t "$EXPERIMENT_NAME:RL.1"
         
         # Apply even-vertical layout to distribute panes evenly
-        tmux select-layout -t "$SESSION_NAME:RL" even-vertical
+        tmux select-layout -t "$EXPERIMENT_NAME:RL" even-vertical
         
         # Set pane titles
-        tmux select-pane -t "$SESSION_NAME:RL.0" -T "Trainer"
-        tmux select-pane -t "$SESSION_NAME:RL.1" -T "Orchestrator"
-        tmux select-pane -t "$SESSION_NAME:RL.2" -T "Inference"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.0" -T "Trainer"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.1" -T "Orchestrator"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.2" -T "Inference"
         
         # Send commands to panes
         # Pane 1: Trainer - stays empty
         
         # Pane 2: Orchestrator
-        tmux send-keys -t "$SESSION_NAME:RL.1" 'while true; do
+        tmux send-keys -t "$EXPERIMENT_NAME:RL.1" 'while true; do
   echo "Waiting for orchestrator log file..."
-  while [ ! -f logs/orchestrator.log ]; do sleep 1; done
+  while [ ! -f logs/'"$EXPERIMENT_NAME"'/orchestrator.log ]; do sleep 1; done
   echo "Following orchestrator.log..."
-  tail -F logs/orchestrator.log
+  tail -F logs/'"$EXPERIMENT_NAME"'/orchestrator.log
 done' C-m
         
         # Pane 3: Inference
-        tmux send-keys -t "$SESSION_NAME:RL.2" 'while true; do
+        tmux send-keys -t "$EXPERIMENT_NAME:RL.2" 'while true; do
   echo "Waiting for inference log file..."
-  while [ ! -f logs/inference.log ]; do sleep 1; done
+  while [ ! -f logs/'"$EXPERIMENT_NAME"'/inference.log ]; do sleep 1; done
   echo "Following inference.log..."
-  tail -F logs/inference.log
+  tail -F logs/'"$EXPERIMENT_NAME"'/inference.log
 done' C-m
         
         # Create second window
-        tmux new-window -t "$SESSION_NAME:2" -n "Monitor"
+        tmux new-window -t "$EXPERIMENT_NAME:2" -n "Monitor"
         
         # Window 2: Monitor - Create horizontal split
-        tmux split-window -h -t "$SESSION_NAME:Monitor"
-        tmux select-layout -t "$SESSION_NAME:Monitor" even-horizontal
+        tmux split-window -h -t "$EXPERIMENT_NAME:Monitor"
+        tmux select-layout -t "$EXPERIMENT_NAME:Monitor" even-horizontal
         
         # Set pane titles and run commands
-        tmux select-pane -t "$SESSION_NAME:Monitor.0" -T "GPU"
-        tmux send-keys -t "$SESSION_NAME:Monitor.0" "nvtop" C-m
+        tmux select-pane -t "$EXPERIMENT_NAME:Monitor.0" -T "GPU"
+        tmux send-keys -t "$EXPERIMENT_NAME:Monitor.0" "nvtop" C-m
         
-        tmux select-pane -t "$SESSION_NAME:Monitor.1" -T "CPU"
-        tmux send-keys -t "$SESSION_NAME:Monitor.1" "htop" C-m
+        tmux select-pane -t "$EXPERIMENT_NAME:Monitor.1" -T "CPU"
+        tmux send-keys -t "$EXPERIMENT_NAME:Monitor.1" "htop" C-m
         
         # Enable pane titles for all windows
-        tmux set-option -t "$SESSION_NAME" -g pane-border-status top
-        tmux set-option -t "$SESSION_NAME" -g pane-border-format " #{pane_title} "
+        tmux set-option -t "$EXPERIMENT_NAME" -g pane-border-status top
+        tmux set-option -t "$EXPERIMENT_NAME" -g pane-border-format " #{pane_title} "
         
         # Also set for each window explicitly
-        tmux set-window-option -t "$SESSION_NAME:RL" pane-border-status top
-        tmux set-window-option -t "$SESSION_NAME:Monitor" pane-border-status top
+        tmux set-window-option -t "$EXPERIMENT_NAME:RL" pane-border-status top
+        tmux set-window-option -t "$EXPERIMENT_NAME:Monitor" pane-border-status
         
         # Select first window and first pane
-        tmux select-window -t "$SESSION_NAME:RL"
-        tmux select-pane -t "$SESSION_NAME:RL.0"
+        tmux select-window -t "$EXPERIMENT_NAME:RL"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.0"
         
         # Switch to the new session
-        tmux switch-client -t "$SESSION_NAME"
+        tmux switch-client -t "$EXPERIMENT_NAME"
     fi
 else
     # Not inside tmux, use attach
-    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
-        echo "Session '$SESSION_NAME' already exists. Attaching..."
-        tmux attach-session -t "$SESSION_NAME"
+    if tmux has-session -t "$EXPERIMENT_NAME" 2>/dev/null; then
+        echo "Session '$EXPERIMENT_NAME' already exists. Attaching..."
+        tmux attach-session -t "$EXPERIMENT_NAME"
     else
-        echo "Creating new tmux session: $SESSION_NAME"
+        echo "Creating new tmux session: $EXPERIMENT_NAME"
         
         # Start new tmux session with first window
-        tmux new-session -d -s "$SESSION_NAME" -n "RL"
+        tmux new-session -d -s "$EXPERIMENT_NAME" -n "RL"
         
         # Window 1: RL - Create 2 more panes for a total of 3
-        tmux split-window -v -t "$SESSION_NAME:RL.0"
-        tmux split-window -v -t "$SESSION_NAME:RL.1"
+        tmux split-window -v -t "$EXPERIMENT_NAME:RL.0"
+        tmux split-window -v -t "$EXPERIMENT_NAME:RL.1"
         
         # Apply even-vertical layout
-        tmux select-layout -t "$SESSION_NAME:RL" even-vertical
+        tmux select-layout -t "$EXPERIMENT_NAME:RL" even-vertical
         
         # Set pane titles
-        tmux select-pane -t "$SESSION_NAME:RL.0" -T "Trainer"
-        tmux select-pane -t "$SESSION_NAME:RL.1" -T "Orchestrator"
-        tmux select-pane -t "$SESSION_NAME:RL.2" -T "Inference"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.0" -T "Trainer"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.1" -T "Orchestrator"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.2" -T "Inference"
         
         # Send commands to panes
         # Pane 2: Orchestrator
-        tmux send-keys -t "$SESSION_NAME:RL.1" 'while true; do
+        tmux send-keys -t "$EXPERIMENT_NAME:RL.1" 'while true; do
   echo "Waiting for orchestrator log file..."
-  while [ ! -f logs/orchestrator.log ]; do sleep 1; done
+  while [ ! -f logs/'"$EXPERIMENT_NAME"'/orchestrator.log ]; do sleep 1; done
   echo "Following orchestrator.log..."
-  tail -F logs/orchestrator.log
+  tail -F logs/'"$EXPERIMENT_NAME"'/orchestrator.log
 done' C-m
         
         # Pane 3: Inference
-        tmux send-keys -t "$SESSION_NAME:RL.2" 'while true; do
+        tmux send-keys -t "$EXPERIMENT_NAME:RL.2" 'while true; do
   echo "Waiting for inference log file..."
-  while [ ! -f logs/inference.log ]; do sleep 1; done
+  while [ ! -f logs/'"$EXPERIMENT_NAME"'/inference.log ]; do sleep 1; done
   echo "Following inference.log..."
-  tail -F logs/inference.log
+  tail -F logs/'"$EXPERIMENT_NAME"'/inference.log
 done' C-m
         
         # Create second window
-        tmux new-window -t "$SESSION_NAME" -n "Monitor"
+        tmux new-window -t "$EXPERIMENT_NAME" -n "Monitor"
         
         # Window 2: Monitor
-        tmux split-window -h -t "$SESSION_NAME:Monitor"
-        tmux select-layout -t "$SESSION_NAME:Monitor" even-horizontal
+        tmux split-window -h -t "$EXPERIMENT_NAME:Monitor"
+        tmux select-layout -t "$EXPERIMENT_NAME:Monitor" even-horizontal
         
         # Set pane titles and run commands
-        tmux select-pane -t "$SESSION_NAME:Monitor.0" -T "GPU"
-        tmux send-keys -t "$SESSION_NAME:Monitor.0" "nvtop" C-m
+        tmux select-pane -t "$EXPERIMENT_NAME:Monitor.0" -T "GPU"
+        tmux send-keys -t "$EXPERIMENT_NAME:Monitor.0" "nvtop" C-m
         
-        tmux select-pane -t "$SESSION_NAME:Monitor.1" -T "CPU"
-        tmux send-keys -t "$SESSION_NAME:Monitor.1" "htop" C-m
+        tmux select-pane -t "$EXPERIMENT_NAME:Monitor.1" -T "CPU"
+        tmux send-keys -t "$EXPERIMENT_NAME:Monitor.1" "htop" C-m
         
         # Enable pane titles for all windows
-        tmux set-option -t "$SESSION_NAME" -g pane-border-status top
-        tmux set-option -t "$SESSION_NAME" -g pane-border-format " #{pane_title} "
+        tmux set-option -t "$EXPERIMENT_NAME" -g pane-border-status top
+        tmux set-option -t "$EXPERIMENT_NAME" -g pane-border-format " #{pane_title} "
         
         # Also set for each window explicitly
-        tmux set-window-option -t "$SESSION_NAME:RL" pane-border-status top
-        tmux set-window-option -t "$SESSION_NAME:Monitor" pane-border-status top
+        tmux set-window-option -t "$EXPERIMENT_NAME:RL" pane-border-status top
+        tmux set-window-option -t "$EXPERIMENT_NAME:Monitor" pane-border-status top
         
         # Select first window and first pane
-        tmux select-window -t "$SESSION_NAME:RL"
-        tmux select-pane -t "$SESSION_NAME:RL.0"
+        tmux select-window -t "$EXPERIMENT_NAME:RL"
+        tmux select-pane -t "$EXPERIMENT_NAME:RL.0"
         
         # Attach to the session
-        tmux attach-session -t "$SESSION_NAME"
+        tmux attach-session -t "$EXPERIMENT_NAME"
     fi
 fi 
\ No newline at end of file

PATCHOF

echo "Patch applied successfully."
