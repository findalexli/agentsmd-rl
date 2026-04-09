#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if grep -q 'def memory_allocated(self)' areal/infra/platforms/cpu.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_engine.py b/areal/engine/fsdp_engine.py
index ccc4a7867..276ce2277 100644
--- a/areal/engine/fsdp_engine.py
+++ b/areal/engine/fsdp_engine.py
@@ -777,7 +777,10 @@ def _create_llm_actor_or_critic(self):

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
-        self.device = torch.device(int(os.environ["LOCAL_RANK"]))
+        if current_platform.device_type == "cpu":
+            self.device = torch.device("cpu")
+        else:
+            self.device = torch.device(int(os.environ["LOCAL_RANK"]))

         dtype = getattr(torch, self.config.dtype)

diff --git a/areal/experimental/engine/archon_engine.py b/areal/experimental/engine/archon_engine.py
index 5a885a6ea..38511d699 100644
--- a/areal/experimental/engine/archon_engine.py
+++ b/areal/experimental/engine/archon_engine.py
@@ -938,7 +938,10 @@ def _get_model_name_parameters(self) -> Iterator[tuple[str, nn.Parameter]]:

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
-        self.device = torch.device(int(os.environ["LOCAL_RANK"]))
+        if current_platform.device_type == "cpu":
+            self.device = torch.device("cpu")
+        else:
+            self.device = torch.device(int(os.environ["LOCAL_RANK"]))

         self.tokenizer = load_hf_tokenizer(self.config.path)

diff --git a/areal/infra/platforms/cpu.py b/areal/infra/platforms/cpu.py
index 20d19d6bd..8c4f08d22 100644
--- a/areal/infra/platforms/cpu.py
+++ b/areal/infra/platforms/cpu.py
@@ -36,3 +36,19 @@ def update_env_vars_for_visible_devices(
     def get_visible_devices(cls) -> list:
         # No-devices for CPU platform
         return []
+
+    def memory_allocated(self) -> int:
+        """No device memory; return 0."""
+        return 0
+
+    def memory_reserved(self) -> int:
+        """No device memory; return 0."""
+        return 0
+
+    def mem_get_info(self) -> tuple[int, int]:
+        """No device memory; return (0, 0)."""
+        return (0, 0)
+
+    def empty_cache(self) -> None:
+        """No-op."""
+        pass
diff --git a/areal/infra/scheduler/local.py b/areal/infra/scheduler/local.py
index a90cf48a1..f74bb6c2a 100644
--- a/areal/infra/scheduler/local.py
+++ b/areal/infra/scheduler/local.py
@@ -630,9 +630,10 @@ def create_workers(self, job: Job, *args, **kwargs) -> list[str]:
                 env = get_env_vars(
                     ",".join([f"{k}={v}" for k, v in scheduling.env_vars.items()]),
                 )
-                env[current_platform.device_control_env_var] = ",".join(
-                    map(str, gpu_devices)
-                )
+                if current_platform.device_control_env_var:
+                    env[current_platform.device_control_env_var] = ",".join(
+                        map(str, gpu_devices)
+                    )

                 thread_env = get_thread_env_vars(
                     cpus_per_task=scheduling.cpu,
diff --git a/examples/math/gsm8k_grpo_cpu.yaml b/examples/math/gsm8k_grpo_cpu.yaml
new file mode 100644
index 000000000..a57c84148
--- /dev/null
+++ b/examples/math/gsm8k_grpo_cpu.yaml
@@ -0,0 +1,174 @@
+# CPU example template: GSM8K GRPO
+# For no-GPU or CPU-only environments; use with a launcher/scheduler that supports CPU.
+
+experiment_name: gsm8k-grpo-cpu
+trial_name: trial0
+
+seed: 1
+enable_offload: false
+total_train_epochs: 1
+tokenizer_path: ${actor.path}
+
+cluster:
+  n_nodes: 1
+  n_gpus_per_node: 0  # CPU template: no GPU
+  fileroot: /tmp/areal/experiments
+  name_resolve:
+    type: nfs
+    nfs_record_root: /tmp/areal/name_resolve
+
+allocation_mode: vllm:d1p1t1+d1p1t1
+
+scheduler:
+  type: null
+
+rollout:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  max_concurrent_rollouts: 16
+  queue_size: null
+  consumer_batch_size: ${train_dataset.batch_size}
+  max_head_offpolicyness: 2
+  enable_rollout_tracing: false
+  scheduling_spec: ${actor.scheduling_spec}
+  fileroot: ${cluster.fileroot}
+  tokenizer_path: ${tokenizer_path}
+  dump_to_file: true
+
+gconfig:
+  n_samples: 2
+  min_new_tokens: 0
+  max_new_tokens: 256
+  greedy: false
+  temperature: 1.0
+
+actor:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  path: Qwen/Qwen2.5-1.5B-Instruct
+  init_from_scratch: false
+  disable_dropout: true
+  gradient_checkpointing: true
+  dtype: bfloat16
+  attn_impl: sdpa
+  mb_spec:
+    max_tokens_per_mb: 2048
+  optimizer:
+    type: adam
+    lr: 1.70e-5
+    weight_decay: 0.017
+    beta1: 0.9
+    beta2: 0.999
+    eps: 1e-8
+    lr_scheduler_type: constant
+    gradient_clipping: 1.0
+    warmup_steps_proportion: 0.001
+  eps_clip: 0.4
+  temperature: ${gconfig.temperature}
+  reward_scaling: 10.0
+  reward_bias: -0.5
+  kl_ctl: 0.0
+  ppo_n_minibatches: 1
+  recompute_logprob: true
+  use_decoupled_loss: true
+  behave_imp_weight_cap: 5.0
+  reward_norm:
+    mean_level: group
+    std_level: group
+    group_size: ${gconfig.n_samples}
+  adv_norm:
+    mean_level: batch
+    std_level: batch
+  weight_update_mode: xccl
+  max_new_tokens: ${gconfig.max_new_tokens}
+  scheduling_spec:
+    - task_type: worker
+      port_count: 2
+      gpu: 0       # CPU template: do not request GPU
+      cpu: 4
+      mem: 8192
+      cmd: python3 -m areal.infra.rpc.rpc_server
+      env_vars: {}
+
+ref:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  path: ${actor.path}
+  init_from_scratch: false
+  disable_dropout: true
+  attn_impl: sdpa
+  dtype: ${actor.dtype}
+  mb_spec:
+    max_tokens_per_mb: 2048
+  optimizer: null
+  scheduling_strategy:
+    type: colocation
+    target: actor
+  scheduling_spec: ${actor.scheduling_spec}
+
+# For vllm usage, install from source: cd to the vllm repo and run pip install -e .
+vllm:
+  model: ${actor.path}
+  seed: ${seed}
+  skip_tokenizer_init: false
+  dtype: ${actor.dtype}
+  max_model_len: 2048
+  gpu_memory_utilization: 0.8
+
+# datasets
+train_dataset:
+  batch_size: 16
+  shuffle: true
+  pin_memory: false
+  num_workers: 0
+  path: openai/gsm8k
+  type: rl
+  max_length: 512
+
+valid_dataset:
+  batch_size: 32
+  pin_memory: false
+  num_workers: 0
+  path: openai/gsm8k
+  type: rl
+
+# Utilities
+saver:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+  freq_epochs: 1
+  freq_steps: null
+  freq_secs: null
+
+recover:
+  mode: disabled
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+  freq_epochs: 1
+  freq_steps: null
+  freq_secs: 3600
+
+evaluator:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+  freq_epochs: 1
+  freq_steps: null
+  freq_secs: null
+
+stats_logger:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+  wandb:
+    mode: disabled
+
+perf_tracer:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+  enabled: false
+  session_tracer:
+    enabled: false

PATCH

echo "Patch applied successfully."
