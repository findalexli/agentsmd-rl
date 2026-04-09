#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (check for distinctive line in new entrypoint)
if grep -q 'def main():' src/prime_rl/entrypoints/inference.py 2>/dev/null && \
   grep -q 'inference(cli(InferenceConfig))' src/prime_rl/entrypoints/inference.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the complete gold patch (code + config changes)
git apply - <<'PATCH'
diff --git a/pyproject.toml b/pyproject.toml
index 74e6cc72ed..f779902a67 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -40,9 +40,9 @@ dependencies = [
 [project.scripts]
 rl = "prime_rl.entrypoints.rl:main"
 sft = "prime_rl.entrypoints.sft:main"
+inference = "prime_rl.entrypoints.inference:main"
 trainer = "prime_rl.trainer.rl.train:main"
 orchestrator = "prime_rl.orchestrator.orchestrator:main"
-inference = "prime_rl.inference.server:main"
 env-server = "prime_rl.orchestrator.env_server.env_server:main"

 [project.entry-points."vllm.general_plugins"]
@@ -90,7 +90,7 @@ torchtitan = { git = "https://github.com/pytorch/torchtitan", rev = "a1fdd7e" }
 dion = { git = "https://github.com/samsja/dion.git", rev = "d891eeb" }
 transformers = { git = "https://github.com/huggingface/transformers.git", rev = "609e3d5" }
 flash-attn-cute = { git = "https://github.com/Dao-AILab/flash-attention.git", subdirectory = "flash_attn/cute", rev = "main" }
-pydantic-config = { git = "https://github.com/samsja/pydantic_config.git", branch = "main" }
+pydantic-config = { git = "https://github.com/samsja/pydantic_config.git", rev = "6990941" }
 reverse-text = { index = "primeintellect" }

 [tool.uv.extra-build-dependencies]
diff --git a/src/prime_rl/entrypoints/inference.py b/src/prime_rl/entrypoints/inference.py
new file mode 100644
index 0000000000..99aead22f0
--- /dev/null
+++ b/src/prime_rl/entrypoints/inference.py
@@ -0,0 +1,117 @@
+import subprocess
+import sys
+from pathlib import Path
+
+import tomli_w
+
+from prime_rl.configs.inference import InferenceConfig
+from prime_rl.utils.config import cli
+from prime_rl.utils.logger import setup_logger
+from prime_rl.utils.pathing import get_config_dir
+
+INFERENCE_TOML = "inference.toml"
+INFERENCE_SBATCH = "inference.sbatch"
+
+
+def write_config(config: InferenceConfig, output_dir: Path, exclude: set[str] | None = None) -> Path:
+    """Write resolved config to disk."""
+    output_dir.mkdir(parents=True, exist_ok=True)
+    config_path = output_dir / INFERENCE_TOML
+    with open(config_path, "wb") as f:
+        tomli_w.dump(config.model_dump(exclude=exclude, exclude_none=True, mode="json"), f)
+    return config_path
+
+
+def write_slurm_script(config: InferenceConfig, config_path: Path, script_path: Path) -> None:
+    """Write the SLURM script to disk."""
+    from jinja2 import Environment, FileSystemLoader
+
+    assert config.slurm is not None
+    assert config.slurm.template_path is not None
+
+    env = Environment(loader=FileSystemLoader(config.slurm.template_path.parent), keep_trailing_newline=True)
+    template = env.get_template(config.slurm.template_path.name)
+
+    script = template.render(
+        config_path=config_path,
+        output_dir=config.output_dir,
+        job_name=config.slurm.job_name,
+        project_dir=config.slurm.project_dir,
+        gpus_per_node=config.deployment.gpus_per_node,
+        partition=config.slurm.partition,
+        num_nodes=config.deployment.num_nodes if config.deployment.type == "multi_node" else 1,
+        port=config.server.port,
+    )
+
+    script_path.parent.mkdir(parents=True, exist_ok=True)
+    script_path.write_text(script)
+
+
+def inference_slurm(config: InferenceConfig):
+    """Run inference via SLURM."""
+    assert config.slurm is not None
+
+    logger = setup_logger("info")
+
+    config_dir = get_config_dir(config.output_dir)
+    exclude = {"deployment", "slurm", "dry_run"} if config.deployment.type == "multi_node" else {"slurm", "dry_run"}
+    config_path = write_config(config, config_dir, exclude=exclude)
+    logger.info(f"Wrote config to {config_path}")
+
+    script_path = config.output_dir / INFERENCE_SBATCH
+    write_slurm_script(config, config_path, script_path)
+    logger.info(f"Wrote SLURM script to {script_path}")
+
+    log_message = (
+        f"Logs:\n"
+        f"  Job:        tail -F {config.output_dir}/job_*.log\n"
+        f"  Inference:  tail -F {config.output_dir}/slurm/latest_infer_node_rank_*.log\n"
+    )
+
+    if config.dry_run:
+        logger.success(f"Dry run complete. To submit manually:\n\n  sbatch {script_path}\n\n{log_message}")
+        return
+
+    logger.info(f"Submitting: sbatch {script_path}")
+    result = subprocess.run(["sbatch", str(script_path)], capture_output=True, text=True)
+    if result.returncode != 0:
+        logger.error(f"sbatch failed: {result.stderr.strip()}")
+        sys.exit(1)
+
+    logger.success(f"{result.stdout.strip()}\n\n{log_message}")
+
+
+def inference_local(config: InferenceConfig):
+    """Run inference locally."""
+    from prime_rl.inference.server import setup_vllm_env
+
+    logger = setup_logger("info")
+
+    if config.dry_run:
+        logger.success("Dry run complete. To start inference locally, remove --dry-run from your command.")
+        return
+
+    host = config.server.host or "0.0.0.0"
+    port = config.server.port
+    logger.info(f"Starting inference on http://{host}:{port}/v1\n")
+
+    setup_vllm_env(config)
+
+    from prime_rl.inference.vllm.server import server  # pyright: ignore
+
+    server(config, vllm_extra=config.vllm_extra)
+
+
+def inference(config: InferenceConfig):
+    if config.slurm is not None:
+        inference_slurm(config)
+    else:
+        inference_local(config)
+
+
+def main():
+    inference(cli(InferenceConfig))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/src/prime_rl/templates/inference.sbatch.j2 b/src/prime_rl/templates/inference.sbatch.j2
new file mode 100644
index 0000000000..531d14f83d
--- /dev/null
+++ b/src/prime_rl/templates/inference.sbatch.j2
@@ -0,0 +1,69 @@
+#!/bin/bash
+
+#SBATCH --job-name={{ job_name }}
+#SBATCH --nodes={{ num_nodes }}
+#SBATCH --ntasks-per-node=1
+#SBATCH --gres=gpu:{{ gpus_per_node }}
+#SBATCH --partition={{ partition }}
+#SBATCH --exclusive
+#SBATCH --output={{ output_dir }}/job_%j.log
+#SBATCH --error={{ output_dir }}/job_%j.log
+
+# Configs
+export NUM_NODES={{ num_nodes }}
+export OUTPUT_DIR={{ output_dir }}
+
+# Infer network interface (IB preferred, fall back to non-virtual eth)
+export INTERFACE=$(ip link show | awk '/^[0-9]+: .* (ib|eth)/ {gsub(":", ""); print $2; exit}')
+export NCCL_SOCKET_IFNAME=${INTERFACE}
+export GLOO_SOCKET_IFNAME=${INTERFACE}
+export VLLM_HOST_IP=$(ip -4 addr show ${INTERFACE} | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
+
+# Redirect logs to latest files for tailing convenience
+mkdir -p {{ output_dir }}/slurm
+ln -sf {{ output_dir }}/job_${SLURM_JOB_ID}.log {{ output_dir }}/slurm/latest_job.log 2>/dev/null || true
+
+run_infer() {
+    local NODE_RANK=$1
+    local PORT={{ port }}
+    local LOG_FILE="{{ output_dir }}/slurm/infer_node_rank_${NODE_RANK}_${SLURM_JOB_ID}.log"
+
+    # Log redirection setup
+    exec > >(tee -a "$LOG_FILE")
+    exec 2>&1
+
+    ln -sf "$LOG_FILE" "{{ output_dir }}/slurm/latest_infer_node_rank_${NODE_RANK}.log" 2>/dev/null || true
+
+    # Set per-node vLLM environment
+    export VLLM_PORT=${PORT}
+    export VLLM_BASE_URL=http://${VLLM_HOST_IP}:${VLLM_PORT}/v1
+
+    echo "[Node ${NODE_RANK}] Starting vLLM on ${VLLM_HOST_IP}:${VLLM_PORT}"
+
+    {% if num_nodes > 1 %}
+    # Multi-node: each node runs independent replica
+    # (no cross-node coordination needed for inference)
+    srun --nodes=1 --ntasks=1 --gres=gpu:{{ gpus_per_node }} \
+        uv run python -m prime_rl.inference.server @ {{ config_path }} &
+    {% else %}
+    # Single-node
+    uv run python -m prime_rl.inference.server @ {{ config_path }}
+    {% endif %}
+}
+
+# Launch inference on each node
+for node_rank in $(seq 0 $((NUM_NODES - 1))); do
+    echo "Launching inference on node ${node_rank}..."
+    run_infer ${node_rank}
+done
+
+# Wait for all background jobs
+wait
+
+echo "Inference job complete."
diff --git a/src/prime_rl/configs/inference.py b/src/prime_rl/configs/inference.py
index 3f9aee24e4..43e1436694 100644
--- a/src/prime_rl/configs/inference.py
+++ b/src/prime_rl/configs/inference.py
@@ -1,10 +1,11 @@
 from argparse import Namespace
-from typing import Annotated, Any, Literal
+from pathlib import Path
+from typing import Annotated, Any, Literal, TypeAlias

-from pydantic import Field, model_validator
+from pydantic import BaseModel, ConfigDict, Field, model_validator
+from pydantic_config import BaseConfig

-from prime_rl.configs.shared import BaseModelConfig
-from prime_rl.utils.config import BaseConfig, get_all_fields
+from prime_rl.configs.shared import BaseModelConfig, SlurmConfig
+from prime_rl.utils.utils import rgetattr, rsetattr
 from prime_rl.utils.utils import rgetattr, rsetattr

 # TODO: Set thinking/ solution budget
@@ -116,6 +117,33 @@ class WeightBroadcastConfig(BaseConfig):
 ]


+class BaseInferenceDeploymentConfig(BaseModel):
+    """Base deployment config for inference."""
+
+    model_config = ConfigDict(extra="forbid")
+
+    gpus_per_node: Annotated[int, Field(description="Number of GPUs per node.")] = 8
+
+
+class SingleNodeInferenceDeploymentConfig(BaseInferenceDeploymentConfig):
+    """Configures a single-node inference deployment."""
+
+    type: Literal["single_node"] = "single_node"
+
+
+class MultiNodeInferenceDeploymentConfig(BaseInferenceDeploymentConfig):
+    """Configures a multi-node inference deployment. Each node runs an independent vLLM replica."""
+
+    type: Literal["multi_node"] = "multi_node"
+
+    num_nodes: Annotated[int, Field(ge=1, description="Number of inference nodes.")] = 2
+
+
+InferenceDeploymentConfig: TypeAlias = Annotated[
+    SingleNodeInferenceDeploymentConfig | MultiNodeInferenceDeploymentConfig, Field(discriminator="type")
+]
+
+
 class InferenceConfig(BaseConfig):
     """Configures inference."""

@@ -244,9 +272,44 @@ class InferenceConfig(BaseConfig):
         ),
     ] = {}

+    # Launcher-only fields
+
+    deployment: Annotated[
+        InferenceDeploymentConfig,
+        Field(
+            description="Deployment configuration for inference.",
+        ),
+    ] = SingleNodeInferenceDeploymentConfig()
+
+    slurm: Annotated[
+        SlurmConfig | None,
+        Field(
+            description="SLURM configuration. If set, the run will be submitted as a SLURM job instead of running locally.",
+        ),
+    ] = None
+
+    output_dir: Annotated[Path, Field(description="Directory for SLURM logs and generated scripts.")] = Path("outputs")
+
+    dry_run: Annotated[bool, Field(description="Only validate and dump resolved configs and exit early.")] = False
+
+    @model_validator(mode="after")
+    def validate_multi_node_requires_slurm(self):
+        if self.deployment.type == "multi_node" and self.slurm is None:
+            raise ValueError("Must use SLURM for multi-node deployment.")
+        return self
+
+    @model_validator(mode="after")
+    def auto_setup_slurm_template(self):
+        if self.slurm is not None and self.slurm.template_path is None:
+            import prime_rl
+
+            templates_dir = Path(prime_rl.__file__).parent / "templates"
+            self.slurm.template_path = templates_dir / "inference.sbatch.j2"
+        return self
+
     @model_validator(mode="after")
-    def round_up_max_lora_rank(self):
-        """Round up max_lora_rank to the nearest valid vLLM value.
+    def auto_setup_max_lora_rank(self):
+        """Auto-setup max_lora_rank by rounding up to the nearest valid vLLM value.

         vLLM only accepts specific values for max_lora_rank: (1, 8, 16, 32, 64, 128, 256, 320, 512).
         This validator ensures that any configured rank is rounded up to the minimum valid value
@@ -307,11 +370,12 @@ def to_vllm(self) -> Namespace:
             "enable_expert_parallel": "enable_expert_parallel",
             "all2all_backend": "all2all_backend",
             "enable_eplb": "enable_eplb",
+            "seed": "seed",
         }

-        for key in get_all_fields(self):
-            value = rgetattr(self, key.replace("-", "_"))
-            rsetattr(namespace, to_vllm.get(key, key), value)
+        for config_key, vllm_key in to_vllm.items():
+            value = rgetattr(self, config_key.replace("-", "_"))
+            rsetattr(namespace, vllm_key, value)

         # Set `logprobs_mode` to `processed_logprobs` by default
         rsetattr(namespace, "logprobs_mode", "processed_logprobs")
# Skill documentation update — this is a key agent config file change
diff --git a/skills/inference-server/SKILL.md b/skills/inference-server/SKILL.md
index 7450c71a71..6cba3d2a61 100644
--- a/skills/inference-server/SKILL.md
+++ b/skills/inference-server/SKILL.md
@@ -20,6 +20,64 @@ uv run inference --model.name Qwen/Qwen3-0.6B --model.max_model_len 2048 --model
 uv run inference @ path/to/config.toml --server.port 8001 --gpu-memory-utilization 0.5
 ```

+## SLURM scheduling
+
+The inference entrypoint supports optional SLURM scheduling, following the same patterns as SFT and RL.
+
+### Single-node SLURM
+
+```toml
+# inference_slurm.toml
+output_dir = "/shared/outputs/my-inference"
+
+[model]
+name = "Qwen/Qwen3-8B"
+
+[parallel]
+tp = 8
+
+[slurm]
+job_name = "my-inference"
+partition = "cluster"
+```
+
+```bash
+uv run inference @ inference_slurm.toml
+```
+
+### Multi-node SLURM (independent vLLM replicas)
+
+Each node runs an independent vLLM instance. No cross-node parallelism — TP and DP must fit within a single node's GPUs.
+
+```toml
+# inference_multinode.toml
+output_dir = "/shared/outputs/my-inference"
+
+[model]
+name = "PrimeIntellect/INTELLECT-3-RL-600"
+
+[parallel]
+tp = 8
+dp = 1
+
+[deployment]
+type = "multi_node"
+num_nodes = 4
+gpus_per_node = 8
+
+[slurm]
+job_name = "my-inference"
+partition = "cluster"
+```
+
+### Dry run
+
+Add `dry_run = true` to generate the sbatch script without submitting:
+
+```bash
+uv run inference @ config.toml --dry-run true
+```
+
 ## Custom endpoints

 The server extends vLLM with:
@@ -43,7 +101,9 @@ curl http://localhost:8000/v1/chat/completions \

 ## Key files

-- `src/prime_rl/inference/server.py` — entry point, env var setup
+- `src/prime_rl/entrypoints/inference.py` — entrypoint with local/SLURM routing
+- `src/prime_rl/inference/server.py` — vLLM env setup
 - `src/prime_rl/configs/inference.py` — `InferenceConfig` and all sub-configs
 - `src/prime_rl/inference/vllm/server.py` — FastAPI routes and vLLM monkey-patches
+- `src/prime_rl/templates/inference.sbatch.j2` — SLURM template (handles both single and multi-node)
 - `configs/debug/infer.toml` — minimal debug config

PATCH

echo "Patch applied successfully."
