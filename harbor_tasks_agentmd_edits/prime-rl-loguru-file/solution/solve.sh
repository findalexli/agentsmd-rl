#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (check for .loguru extension in rl.py)
if grep -q 'rl.loguru' src/prime_rl/rl.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full patch including code and README changes
git apply - <<'PATCH'
diff --git a/.tmuxinator.yaml b/.tmuxinator.yaml
index 1b82a17338..456453635b 100644
--- a/.tmuxinator.yaml
+++ b/.tmuxinator.yaml
@@ -2,29 +2,25 @@ name: rl
 enable_pane_titles: true

 windows:
-  - Entrypoint:
-      layout: even-vertical
-      panes:
-        - Inference:
-        - RL:
-  - Training:
+  - RL:
       layout: even-vertical
       panes:
+        - Trainer:
         - Orchestrator:
           - |
             while true; do
               echo "Waiting for orchestrator log file..."
               while [ ! -f logs/orchestrator.log ]; do sleep 1; done
               echo "Following orchestrator.log..."
-              tail -F logs/orchestrator.log
+              tail -F logs/orchestrator.loguru
             done
-        - Trainer:
+        - Inference:
           - |
             while true; do
               echo "Waiting for trainer log file..."
-              while [ ! -f logs/trainer.log ]; do sleep 1; done
-              echo "Following trainer.log..."
-              tail -F logs/trainer.log
+              while [ ! -f logs/inference.log ]; do sleep 1; done
+              echo "Following inference.log..."
+              tail -F logs/inference.log
             done
   - Monitor:
       layout: even-horizontal
diff --git a/README.md b/README.md
index 9e3abb8fab..9c33347c31 100644
--- a/README.md
+++ b/README.md
@@ -118,28 +118,7 @@ ulimit -n 32000

 ### RL

-We provide a convenience endpoint `rl` for single-node RL experiments. It configures and startsthe trainer, orchestrator and, optionally, an inference server. It enforces correctly setting shared configs (e.g. the model name or async level should be the same across all modules) and dispatches and monitors subprocesses. To stream the logs from each module, we use file logging which can be automatically viewed from a `tmux` layout defined in `.tmuxinator.yaml`. The recommended workflow is:
-
-1. Start a pre-layouted `tmux` session using `tmuxinator`
-
-```bash
-tmuxinator
-```
-
-2. Start the inference server separately in the `Inference` pane (to keep it alive across experiments with the same model)
-
-```bash
-uv run inference @ configs/inference/reverse_text.toml
-```
-
-3. Start the trainer and orchestrator in the `RL` pane.
-
-```bash
-uv run rl \
-  --trainer @ configs/trainer/reverse_text.toml \
-  --orchestrator @ configs/orchestrator/reverse_text.toml
-```
-
+We provide a convenience endpoint `rl` for single-node RL experiments. It configures and startsthe trainer, orchestrator and, optionally, an inference server. It enforces correctly setting shared configs (e.g. the model name or async level should be the same across all modules) and dispatches and monitors subprocesses. To stream the logs from each module, we use file logging, by default only the trainer logs will be displayed on the main process.

 **Reverse Text**

@@ -183,6 +162,50 @@ uv run rl \
 *NB: This setup requires 8 GPUs - 2 are used for the FSDP trainer, 6 are used for inference with TP=2 and DP=3.*


+### Tmuxinator
+
+
+ We also provide a convenient tmuxinator layout to start a run and view all the logs at the same time. The recommended workflow is:
+
+1. Start a pre-layouted `tmux` session using `tmuxinator`
+
+```bash
+tmuxinator
+```
+
+2. Start the trainer and orchestrator in the `Trainer` pane.
+
+```bash
+uv run rl \
+  --trainer @ configs/trainer/reverse_text.toml \
+  --orchestrator @ configs/orchestrator/reverse_text.toml \
+  --inference @ configs/inference/reverse_text.toml
+```
+
+#### Standalone Inference Server
+You can optionally start the inference server individually to avoid the long vllm warmup at each run restart. Useful for development.
+
+1. Start the pre-layouted `tmux` session using `tmuxinator`
+
+```bash
+tmuxinator
+```
+
+2. Start the inference server in the `Inference` pane.
+
+```bash
+uv run inference @ configs/inference/reverse_text.toml
+```
+
+3. You can now start the trainer and orchestrator in the `Trainer` pane.
+
+```bash
+uv run rl \
+  --trainer @ configs/trainer/reverse_text.toml \
+  --orchestrator @ configs/orchestrator/reverse_text.toml \
+```
+
+
 ### Evals

 *TBD*
diff --git a/src/prime_rl/orchestrator/logger.py b/src/prime_rl/orchestrator/logger.py
index 1ecb097e93..389b9e7269 100644
--- a/src/prime_rl/orchestrator/logger.py
+++ b/src/prime_rl/orchestrator/logger.py
@@ -18,7 +18,7 @@ def setup_logger(log_config: LogConfig) -> Logger:

     # Setup the logger handlers
     if log_config.path:
-        log_config.path = Path(log_config.path.as_posix() + ".log")
+        log_config.path = Path(log_config.path.as_posix() + ".loguru")
     logger = setup_handlers(loguru_logger, format, log_config, rank=0)
     set_logger(logger)

diff --git a/src/prime_rl/rl.py b/src/prime_rl/rl.py
index 95a45e04d8..86915aa1f1 100644
--- a/src/prime_rl/rl.py
+++ b/src/prime_rl/rl.py
@@ -176,7 +176,8 @@ def setup_logger(log_config: LogConfig) -> Logger:

     # Setup the logger handlers
     format = format_time(log_config) + format_message()
-    log_config.path = log_config.path / "rl.log"
+    log_config.path = log_config.path / "rl.loguru"
+
     logger = setup_handlers(loguru_logger, format, log_config, rank=0)
     set_logger(logger)

@@ -226,7 +227,7 @@ def rl(config: RLConfig):

         # Cleaning logs
         logger.info(f"Cleaning logs ({config.log.path})")
-        for log_file in config.log.path.glob("*.log|*.stdout"):
+        for log_file in config.log.path.glob("*.log|*.log"):
             log_file.unlink(missing_ok=True)

         # Cleaning checkpoints
@@ -359,7 +360,9 @@ def rl(config: RLConfig):

         # Monitor all processes for failures
         logger.success("Startup complete. Showing trainer logs...")
-        Popen(["tail", "-F", "logs/trainer.log"])
+
+        tail_process = Popen(["tail", "-F", "logs/trainer.log"])
+        processes.append(tail_process)

         # Check for errors from monitor threads
         while not (stop_events["orchestrator"].is_set() and stop_events["trainer"].is_set()):
diff --git a/src/prime_rl/trainer/logger.py b/src/prime_rl/trainer/logger.py
index f80706810f..a3b9f56ad6 100644
--- a/src/prime_rl/trainer/logger.py
+++ b/src/prime_rl/trainer/logger.py
@@ -21,7 +21,7 @@ def setup_logger(log_config: LogConfig, world: World) -> Logger:
     if log_config.path:
         if world.world_size > 1 and world.local_rank > 0:
             log_config.path = Path(log_config.path.as_posix() + str(world.local_rank))
-        log_config.path = Path(log_config.path.as_posix() + ".log")
+        log_config.path = Path(log_config.path.as_posix() + ".loguru")
     logger = setup_handlers(loguru_logger, format, log_config, rank=world.rank)
     set_logger(logger)

PATCH

echo "Patch applied successfully."
