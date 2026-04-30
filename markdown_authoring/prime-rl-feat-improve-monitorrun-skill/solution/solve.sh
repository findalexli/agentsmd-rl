#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency guard
if grep -qF "The output directory and tmux session name are typically provided by the researc" "skills/monitor-run/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/monitor-run/SKILL.md b/skills/monitor-run/SKILL.md
@@ -3,59 +3,93 @@ name: monitor-run
 description: How to monitor ongoing training runs — find output directories, check logs, diagnose performance, and inspect SLURM jobs. Use when asked to check on a run, debug training issues, or investigate performance.
 ---
 
-# Monitor a Run
+# Monitor RL Run
 
-## Find the output directory
+## Runbook
 
-The output directory is set in the config (`output_dir`). To find it:
+### On launch
 
-- **Local run**: check the resolved configs at `{output_dir}/configs/`
-- **SLURM run**: check `squeue -u $USER` to find the job, then look at `{output_dir}/configs/`
+Immediately gather context and write a summary of the run into `{output_dir}/STATUS.md`:
 
-## RL
+1. Identify the output directory and read the resolved configs to understand the experiment (model, envs, hyperparameters, deployment details).
+2. Make sure that the run started successfully and that all processes are alive.
+3. Read the logs and note the current training step and health.
 
-### Check GPU allocation
+### Recurring check-ins
 
-#### Single-node
+After the initial overview, schedule recurring check-ins. By default, check in every **1 hour** (the researcher can override this).
 
-GPUs are assigned in order: inference first, then trainer, then teacher (if any).
+At each check-in:
 
+1. Check that all processes are alive.
+2. Read the logs — look for errors, warnings, hangs, or degraded performance
+3. Note the current training step, key metrics, and checkpoint progress.
+4. **Append an entry to `{output_dir}/STATUS.md`**:
+
+```markdown
+## YYYY-MM-DD HH:MM UTC
+
+**Step**: {current_step} / {max_steps}
+**Health**: {Healthy | Degraded | Down}
+
+**Progress**: reward/mean, seq_len, truncation rate, eval scores (if available), notable env-specific metrics.
+**Stability**: entropy, mismatch KL, grad norm — flag any spikes or concerning trends.
+**Performance**: trainer and orchestrator step times, who is waiting on whom, env server lag, inference pressure.
+
+**Notes**: (anything unusual — errors, restarts, hangs, etc. Omit if nothing notable.)
 ```
-GPU 0..N-1     → inference (vLLM)
-GPU N..M-1     → trainer (torchrun)
-GPU M..K-1     → teacher inference (optional)
-```
 
-The exact split is controlled by `deployment.num_infer_gpus`, `deployment.num_train_gpus`, and `deployment.num_teacher_gpus`. The orchestrator runs as a separate process (no GPU). Check the resolved configs at `{output_dir}/configs/` for the actual values.
+Always append — never overwrite previous entries.
+
+### Restarting a run
+
+**IMPORTANT**: Never restart a run unless you were explicitly instructed by the researcher. If you were given permission, make sure to ask the researcher for the exact command to resume a run and under what conditions a restart is necessary.
 
-#### Multi-node (SLURM)
+**IMPORTANT**: Never run kill or launch commands directly from your shell. Instead, send them to the tmux **Launcher** window so the researcher can see exactly what was executed.
+
+Use `tmux send-keys` to dispatch commands to the Launcher pane:
 
 ```bash
-squeue -u $USER -o "%.18i %.9P %.30j %.8T %.10M %.6D %R"
+# Get your current tmux session name
+SESSION=$(tmux display-message -p '#S')
+
+# Send a command to the Launcher window
+tmux send-keys -t "$SESSION:Launcher" 'your command here' Enter
 ```
 
-Nodes from the SLURM allocation are split in order: inference nodes first, then trainer nodes.
+After a restart, verify that all processes are back up and healthy before resuming periodic check-ins. Check the process tree and tail the logs to confirm the run is making progress again.
 
-```
-Nodes 0..I-1   → inference (vLLM, first node of each replica also runs vllm-router)
-Nodes I..I+T-1 → trainer (torchrun, rank 0 node also runs the orchestrator)
-```
+---
+
+## Reference
+
+### Output directory and tmux session
 
-The node assignment is visible in the generated sbatch script at `{output_dir}/rl.sbatch`.
+The output directory and tmux session name are typically provided by the researcher in the appended system prompt (see `scripts/tmux.sh` — the Claude window is launched with this context). If not provided, **ask the researcher** which output directory to monitor and which tmux session the run is in.
 
-### Check logs
+The tmux session contains the **Launcher** window where the researcher runs launch commands — this is where you should send any restart commands (see [Restarting a run](#restarting-a-run)).
 
-Log paths are consistent across deployment types — `logs/trainer.log` and `logs/inference.log` always exist (real files for local, symlinks for multi-node SLURM).
+Once you have the output directory, the resolved configs are at `{output_dir}/configs/`.
 
-#### Local runs
+### Configs
+
+The launcher writes resolved configs as TOML files to `{output_dir}/configs/`. Read `rl.toml` to get the full picture of the experiment (model, envs, hyperparameters, wandb, deployment).
+
+### Logs
+
+Logs are usually the most informative place to monitor a run.
 
 ```
 {output_dir}/logs/
-├── trainer.log                  # trainer stdout (rank 0 only)
+├── trainer.log                  # trainer stdout (rank 0)
 ├── orchestrator.log             # orchestrator stdout
 ├── inference.log                # vLLM inference server stdout
 ├── trainer/
+│   ├── node_*.log               # per-node logs (multi-node only)
 │   └── torchrun/                # per-rank stdout/stderr (all ranks)
+├── inference/
+│   ├── node_*.log               # per-node logs (multi-node only)
+│   └── router_0.log             # vllm-router per replica (multi-node only)
 └── envs/
     ├── train/{env_name}/
     │   ├── env_server.log
@@ -64,61 +98,118 @@ Log paths are consistent across deployment types — `logs/trainer.log` and `log
         └── ...
 ```
 
-#### SLURM runs
+Usually it's sufficient to tail `trainer.log`, `orchestrator.log`, and `inference.log`. For debugging, it may be necessary to check the per-node logs (`node_*.log`) or per-rank trainer logs under `torchrun/`.
 
+```bash
+tail {output_dir}/logs/trainer.log                     # training progress — kl mismatch, entropy, grad norm, trainer step time
+tail {output_dir}/logs/orchestrator.log                # orchestrator — reward, rollouts, env execution, inference step time
+tail {output_dir}/logs/inference.log                   # inference — completed HTTP requests, engine stats, OOM errors
+tail {output_dir}/logs/envs/train/*/env_server.log     # env server — aggregated stats across its workers (lag, task distribution)
+tail {output_dir}/logs/envs/train/*/env_worker_*.log   # env workers — individual env logs
 ```
-{output_dir}/logs/
-├── trainer.log                  -> trainer/node_0.log (symlink)
-├── inference.log                -> inference/node_0.log (symlink)
-├── orchestrator.log
-├── trainer/
-│   ├── node_0.log
-│   ├── node_1.log
-│   └── torchrun/               # per-rank stdout/stderr (all ranks)
-├── inference/
-│   ├── node_0.log
-│   ├── node_1.log
-│   └── router_0.log            # vllm-router per replica
-└── envs/
-    └── ...
+
+All logs use loguru with the format `HH:mm:ss  LEVEL message`. Log levels: `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`. To scan for problems:
+
+```bash
+grep -E "WARNING|ERROR" {output_dir}/logs/trainer.log
+grep -E "WARNING|ERROR" {output_dir}/logs/orchestrator.log
+grep -E "WARNING|ERROR" {output_dir}/logs/inference.log
+grep -E "WARNING|ERROR" {output_dir}/logs/envs/train/*/env_server.log
+grep -E "WARNING|ERROR" {output_dir}/logs/envs/train/*/env_worker_*.log
 ```
 
-### Identify processes via process tree
+### Metrics
 
-All prime-rl and verifiers processes set custom process titles using `setproctitle`, making them easy to identify in `ps`, `htop`, and `pstree`.
+All metrics below are logged to the console. The source column indicates which log file to check.
 
-#### Process titles
+#### Progress
 
-| Process | Title |
-|---------|-------|
-| RL launcher (`uv run rl`) | `PRIME-RL::Launcher` |
-| SFT launcher (`uv run sft`) | `PRIME-RL::SFT` |
-| Inference server (`uv run inference`) | `PRIME-RL::Inference` |
-| Orchestrator (`uv run orchestrator`) | `PRIME-RL::Orchestrator` |
-| RL trainer (via torchrun) | `PRIME-RL::Trainer` |
-| SFT trainer (via torchrun) | `PRIME-RL::SFTTrainer` |
-| Env server (`uv run env-server`) | `PRIME-RL::EnvServer` |
-| vLLM engine core (spawned by inference) | `VLLM::EngineCore` |
-| Env server (spawned by orchestrator) | `Verifiers::EnvServer` |
-| Env worker N | `Verifiers::EnvWorker{N}` |
+These tell you whether the model is learning and how the run is progressing.
 
-#### Inspecting the process tree
+| Metric | Source | Description |
+|--------|--------|-------------|
+| `reward/{all,env}/mean` | orchestrator | mean training reward |
+| `seq_len/{all,env}/mean` | orchestrator | average sequence length in tokens |
+| `num_turns/{all,env}/mean` | orchestrator | average turns per rollout (ignore for single-turn envs) |
+| `is_truncated/{all,env}/mean` | orchestrator | fraction of truncated rollouts |
+| `empty_rollouts/{all,env}` | orchestrator | fraction of empty rollouts |
+| `errored_rollouts/{all,env}` | orchestrator | fraction of errored rollouts |
+| `metrics/{env}/{metric}` | orchestrator | env-specific metrics (e.g. pass rate for unit tests) |
+| `eval/{env}/{avg@k,pass@k}` | orchestrator | eval scores (if eval is configured) |
 
-```bash
-# Find all prime-rl / verifiers processes
-ps -eo pid,comm,args | grep -E "PRIME-RL|Verifiers"
+#### Stability
+
+These tell you whether training is healthy or diverging.
 
-# Show the full tree from the launcher PID (filter threads with grep -v)
-pstree -ap <launcher_pid> | grep -v '{.*}'
+| Metric | Source | Description |
+|--------|--------|-------------|
+| `mismatch_kl/mean` | trainer | KL divergence between trainer and (old) inference policy  |
+| `entropy/mean` | trainer | policy entropy |
+| `optim/grad_norm` | trainer | gradient norm — spikes may precede divergence |
 
-# Find vLLM processes specifically (engine core, router)
-ps -eo pid,comm,args | grep -E "VLLM::"
+#### Performance
 
-# Find vLLM processes on GPUs
-nvidia-smi --query-compute-apps=pid,name,gpu_uuid --format=csv,noheader
+These tell you how fast the run is and where the bottlenecks are. Trainer and orchestrator step independently — compare their step times to identify who is waiting on whom.
+
+**Trainer** (in `trainer.log`):
+
+| Metric | Description |
+|--------|-------------|
+| `time/step` | total trainer step time |
+| `time/wait_for_batch` | time waiting for orchestrator to deliver a batch — **high = orchestrator is the bottleneck** |
+| `time/forward_backward` | forward/backward pass time |
+| `time/broadcast_weights` | time broadcasting weights to inference |
+| `time/save_ckpt` | checkpoint save time |
+| `perf/throughput` | tokens/s throughput |
+| `perf/mfu` | model FLOPs utilization % |
+
+**Orchestrator** (in `orchestrator.log`):
+
+| Metric | Description |
+|--------|-------------|
+| `time/step` | total orchestrator step time |
+| `time/generate_completions` | rollout generation time |
+| `time/wait_for_ckpt` | time waiting for trainer checkpoint — **high = trainer is the bottleneck** |
+| `time/update_weights` | weight update time |
+| `scheduler/async_level` | current async level |
+| `scheduler/inflight_rollouts` | number of in-flight rollouts |
+
+**Env servers** (in `envs/train/{env_name}/env_server.log`):
+
+| Metric | Description |
+|--------|-------------|
+| event loop lag (min/mean/p90/p99/max) | server and worker lag stats, logged periodically |
+| active task distribution | per-worker and per-env task counts  |
+
+**Inference** (in `inference.log`):
+
+vLLM logs completed HTTP requests and occasionally engine stats. For live inference metrics, query the vLLM metrics endpoint directly:
+
+```bash
+# Get vLLM Prometheus metrics (num running/queued reqs, KV cache usage, etc.)
+curl -s http://localhost:8000/metrics | grep -E "num_requests|gpu_cache_usage"
 ```
 
-A typical single-node RL run process tree:
+Key vLLM metrics to watch:
+- `vllm:num_requests_running` — requests currently being processed
+- `vllm:num_requests_waiting` — requests queued waiting for KV cache space
+- `vllm:gpu_cache_usage_perc` — KV cache pressure (approaching 1.0 = requests will queue)
+
+### Errors and warnings
+
+As part of every check-in, grep all logs for `WARNING` and `ERROR` level messages. Pay special attention to env server and env worker logs — these are the most common source of issues since they run user-provided code.
+
+Common things to look for:
+- **Env workers**: exceptions in environment execution, timeouts, sandbox errors, OOM kills
+- **Orchestrator**: empty/errored rollout spikes, weight broadcast failures, checkpoint errors
+- **Trainer**: NCCL/CUDA errors, OOM, NaN loss or gradients
+- **Inference**: NCCL/CUDA errors, OOM, request timeouts
+
+A small number of warnings is normal (e.g. occasional env timeouts). Escalate to the researcher if you see errors that are persistent, increasing, or affect a large fraction of rollouts.
+
+### Processes
+
+All processes have custom process names, making them easy to identify in `ps`, `htop`, and `pstree`. Use this in case you need to debug a process that is not responding or behaving unexpectedly.
 
 ```
 PRIME-RL::Launcher
@@ -131,47 +222,8 @@ PRIME-RL::Launcher
 │   └── ...
 ├── torchrun
 │   └── PRIME-RL::Trainer        (RL trainer, GPU 1+)
-└── tail -F trainer.log
-```
-
-### Check performance
-
-#### Trainer
-
-Check `{output_dir}/logs/trainer.log` (rank 0, node 0). For multi-node, per-node logs are at `logs/trainer/node_*.log`. Per-rank logs from all ranks are under `logs/trainer/torchrun/`.
-
-Key metrics per step:
-- `time/step` — total step time
-- `time/wait_for_batch` — time waiting for the orchestrator to deliver a batch
-- `time/forward_backward` — forward/backward pass time
-- `time/broadcast_weights` — time broadcasting weights to inference servers
-- `time/save_ckpt` — checkpoint save time
-
-High `wait_for_batch` means the orchestrator is the bottleneck (slow rollouts, slow envs, or too few inference replicas).
-
-#### Orchestrator
-
-Check `{output_dir}/logs/orchestrator.log`.
-
-Key metrics per step:
-- `time/step` — total orchestrator step time
-- `time/generate_completions` — rollout generation time
-- `time/wait_for_ckpt` — time waiting for trainer checkpoint
-- `time/update_weights` — weight update time
-- `scheduler/async_level` — current async level
-- `empty_rollouts/all` — fraction of empty rollouts
-- `errored_rollouts/all` — fraction of errored rollouts
-
-High `wait_for_ckpt` means the trainer is the bottleneck. The orchestrator logs when it pauses/resumes:
-```
-"Orchestrator paused: waiting for trainer process to complete checkpoint ..."
-"Orchestrator resumed: checkpoint ... ready (after ...s)"
+└── tail trainer.log
 ```
 
-#### Env servers
-
-Check `{output_dir}/logs/envs/train/{env_name}/env_server.log` and `{output_dir}/logs/envs/train/{env_name}/env_worker_{id}.log`.
+For multi-node runs, trainer and inference processes are distributed across separate nodes. Use `srun` or `ssh` to inspect processes on other nodes directly.
 
-Key things to look for:
-- **Event loop lag**: server logs aggregate lag stats (min/mean/median/p90/p99/max) of itself and all workers periodically. check that neither is overloaded
-- **Active task distribution**: check if tasks are distributed as expected across workers per-env and across envs. uneven distribution suggests some workers/envs are slower. heavily skewed distribution can indicate that a env is bottlenecking the trainer or has stopped being responsive.
PATCH

echo "Gold patch applied."
