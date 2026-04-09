#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if [ -f "areal/tests/grpo/config_megatron.yaml" ]; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'PATCH'
diff --git a/areal/tests/grpo/config.yaml b/areal/tests/grpo/config_fsdp.yaml
similarity index 100%
rename from areal/tests/grpo/config.yaml
rename to areal/tests/grpo/config_fsdp.yaml
diff --git a/areal/tests/grpo/config_megatron.yaml b/areal/tests/grpo/config_megatron.yaml
new file mode 100644
index 000000000..f6f3d29e7
--- /dev/null
+++ b/areal/tests/grpo/config_megatron.yaml
@@ -0,0 +1,75 @@
+experiment_name: tests-grpo
+trial_name: trial
+cluster:
+  n_nodes: 1
+  n_gpus_per_node: 2
+  fileroot: /tmp/areal/experiments
+allocation_mode: sglang:d1+megatron:d1
+seed: 1
+total_train_epochs: 1
+total_train_steps: 16
+tokenizer_path: ${actor.path}
+train_dataset:
+  path: openai/gsm8k
+  batch_size: 64
+  max_length: 512
+  type: rl
+saver:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+evaluator:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+stats_logger:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+recover:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+sglang:
+  model_path: ${actor.path}
+  random_seed: ${seed}
+launcher: {}
+gconfig:
+  n_samples: 4
+  max_new_tokens: 1024
+
+rollout:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  consumer_batch_size: ${train_dataset.batch_size}
+
+actor:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  path: Qwen/Qwen3-0.6B
+  mb_spec:
+    max_tokens_per_mb: 4096
+  optimizer:
+    type: adam
+    lr: 3e-6
+    weight_decay: 0.003
+    beta1: 0.9
+    beta2: 0.999
+    eps: 1e-8
+    lr_scheduler_type: constant
+    gradient_clipping: 1.0
+    warmup_steps_proportion: 0.001
+  group_size: ${gconfig.n_samples}
+  recompute_logprob: true
+  use_decoupled_loss: true
+  kl_ctl: 0.0
+  adv_norm:
+    mean_level: batch
+    std_level: batch
+
+ref:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  path: ${actor.path}
+  mb_spec:
+    max_tokens_per_mb: 4096
diff --git a/areal/tests/grpo/test_grpo.py b/areal/tests/grpo/test_grpo.py
index ef064c6bf..c672addd3 100644
--- a/areal/tests/grpo/test_grpo.py
+++ b/areal/tests/grpo/test_grpo.py
@@ -3,6 +3,7 @@
 import sys
 from dataclasses import asdict

+import pytest
 import yaml
 from sh import Command

@@ -10,13 +11,13 @@
 from areal.tests.utils import get_dataset_path, get_model_path


-def test_grpo(tmp_path: str):
+@pytest.mark.parametrize("backend", ["fsdp", "megatron"])
+def test_grpo(tmp_path: str, backend: str) -> None:
     base_dir = os.path.dirname(os.path.abspath(__file__))
+    config_path = os.path.join(base_dir, f"config_{backend}.yaml")

     # Wrap over the original config to use local models/datasets if possible
-    config, _ = load_expr_config(
-        ["--config", os.path.join(base_dir, "config.yaml")], GRPOConfig
-    )
+    config, _ = load_expr_config(["--config", config_path], GRPOConfig)

     # Use get_model_path to check local or download from HuggingFace
     local_model_path = config.actor.path.replace("/", "__")
diff --git a/areal/tests/sft/config.yaml b/areal/tests/sft/config_fsdp.yaml
similarity index 100%
rename from areal/tests/sft/config.yaml
rename to areal/tests/sft/config_fsdp.yaml
diff --git a/areal/tests/sft/config_megatron.yaml b/areal/tests/sft/config_megatron.yaml
new file mode 100644
index 000000000..f5fa0c84a
--- /dev/null
+++ b/areal/tests/sft/config_megatron.yaml
@@ -0,0 +1,46 @@
+experiment_name: tests-sft
+trial_name: trial
+cluster:
+  n_nodes: 1
+  n_gpus_per_node: 1
+  fileroot: /tmp/areal/experiments
+allocation_mode: megatron:d1
+seed: 1
+total_train_epochs: 1
+total_train_steps: 16
+tokenizer_path: ${model.path}
+train_dataset:
+  type: sft
+  path: openai/gsm8k
+  batch_size: 16
+saver:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+evaluator:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+stats_logger:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+recover:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  fileroot: ${cluster.fileroot}
+launcher: {}
+
+model:
+  experiment_name: ${experiment_name}
+  trial_name: ${trial_name}
+  path: Qwen/Qwen3-0.6B
+  optimizer:
+    type: adam
+    lr: 3e-6
+    weight_decay: 0.003
+    beta1: 0.9
+    beta2: 0.95
+    eps: 1e-5
+    lr_scheduler_type: cosine
+    gradient_clipping: 1.0
diff --git a/areal/tests/sft/ref_losses.json b/areal/tests/sft/ref_losses_fsdp.json
similarity index 100%
rename from areal/tests/sft/ref_losses.json
rename to areal/tests/sft/ref_losses_fsdp.json
diff --git a/areal/tests/sft/ref_losses_megatron.json b/areal/tests/sft/ref_losses_megatron.json
new file mode 100644
index 000000000..c7909ad3a
--- /dev/null
+++ b/areal/tests/sft/ref_losses_megatron.json
@@ -0,0 +1,18 @@
+[
+    1.4310507774353027,
+    1.2983919382095337,
+    1.461419701576233,
+    1.202308177947998,
+    1.2124967575073242,
+    1.0914961099624634,
+    1.1028367280960083,
+    1.0901871919631958,
+    1.081791639328003,
+    1.105497121810913,
+    1.0020147562026978,
+    1.1141692399978638,
+    0.9268699884414673,
+    0.9272167682647705,
+    0.9887491464614868,
+    0.8537970781326294
+]
diff --git a/areal/tests/sft/test_sft.py b/areal/tests/sft/test_sft.py
index dd70cf0a1..6bcf84444 100644
--- a/areal/tests/sft/test_sft.py
+++ b/areal/tests/sft/test_sft.py
@@ -11,13 +11,14 @@
 from areal.tests.utils import get_dataset_path, get_model_path


-def test_sft(tmp_path: str):
+@pytest.mark.parametrize("backend", ["fsdp", "megatron"])
+def test_sft(tmp_path: str, backend: str) -> None:
     base_dir = os.path.dirname(os.path.abspath(__file__))
+    config_path = os.path.join(base_dir, f"config_{backend}.yaml")
+    ref_losses_path = os.path.join(base_dir, f"ref_losses_{backend}.json")

     # Wrap over the original config to use local models/datasets if possible
-    config, _ = load_expr_config(
-        ["--config", os.path.join(base_dir, "config.yaml")], SFTConfig
-    )
+    config, _ = load_expr_config(["--config", config_path], SFTConfig)

     # Use get_model_path to check local or download from HuggingFace
     local_model_path = config.model.path.replace("/", "__")
@@ -64,7 +65,7 @@ def test_sft(tmp_path: str):
     with open(os.path.join(tmp_path, "losses.json")) as f:
         losses: list[float] = json.load(f)

-    with open(os.path.join(base_dir, "ref_losses.json")) as f:
+    with open(ref_losses_path) as f:
         ref_losses: list[float] = json.load(f)

     # Refer to https://docs.pytorch.org/docs/stable/testing.html#torch.testing.assert_close
diff --git a/docs/cli_reference.md b/docs/cli_reference.md
index 84596b044..d848df0aa 100644
--- a/docs/cli_reference.md
+++ b/docs/cli_reference.md
@@ -369,6 +369,9 @@ Configuration for PPO actor model, a subclass of a TrainEngine.
 | `adv_norm`                  | [`NormConfig`](section-norm) \| None                | `None`                | Normalization configuration for advantages.                                                                                                                                                                                                                                                                                                                                                                                                                  |
 | `kl_ctl`                    | float                                               | `0.1`                 | KL divergence coefficient                                                                                                                                                                                                                                                                                                                                                                                                                                    |
 | `kl_estimator`              | string                                              | `"k1"`                | KL divergence estimator **Choices:** `k1`, `k2`, `k3`                                                                                                                                                                                                                                                                                                                                                                                                        |
+| `use_sapo_loss`             | boolean                                             | `False`               | Use SAPO loss (mutually exclusive with PPO clipping)                                                                                                                                                                                                                                                                                                                                                                                                         |
+| `sapo_tau_pos`              | float                                               | `1.0`                 | SAPO temperature for positive advantages                                                                                                                                                                                                                                                                                                                                                                                                                     |
+| `sapo_tau_neg`              | float                                               | `1.05`                | SAPO temperature for negative advantages                                                                                                                                                                                                                                                                                                                                                                                                                     |
 | `recompute_logprob`         | boolean                                             | `False`               | Recompute log probability and replace the log probability returned by inference.                                                                                                                                                                                                                                                                                                                                                                             |
 | `use_decoupled_loss`        | boolean                                             | `False`               | Use the decoupled loss. Implicitly enables recompute_logprob.                                                                                                                                                                                                                                                                                                                                                                                                |
 | `behav_imp_weight_cap`      | float \| None                                       | `None`                | Filter out tokens where behav_imp_weight exceeds behav_imp_weight_cap when computing loss. Must be > 1.0. use_decoupled_loss must be true.                                                                                                                                                                                                                                                                                                                   |
diff --git a/examples/experimental/proxy/README.md b/examples/experimental/proxy/README.md
index 4a4467a37..44ccfeefc 100644
--- a/examples/experimental/proxy/README.md
+++ b/examples/experimental/proxy/README.md
@@ -13,13 +13,15 @@ trial_name=run1
 ```

 This script will run the example agent in `gsm8k_agent.py`. You can also modify
-agent_module_path to `gsm8k_multi_turn_agent`, `gsm8k_openai_agent`, `math_with_python_tool` or `multi_agent_math` to run other example agents.
+agent_module_path to `gsm8k_multi_turn_agent`, `gsm8k_openai_agent`,
+`math_with_python_tool` or `multi_agent_math` to run other example agents.

 ## Write Your Own Agent

-1. Write an Agent that calls OpenAI-compatible APIs (e.g. chat completions, responses) using a framework that you are familiar with, such as
+1. Write an Agent that calls OpenAI-compatible APIs (e.g. chat completions, responses)
+   using a framework that you are familiar with, such as
    [OpenAI Agent](https://openai.github.io/openai-agents-python/)
-2. Write an AReaL interface function named `run_agent_return_reward`, where the input
+1. Write an AReaL interface function named `run_agent_return_reward`, where the input
    data is a piece of data in the dataset, and the function needs to return a float
    representing the final reward:

@@ -35,7 +37,9 @@ async def run_agent_return_reward(data: Any) -> float:
     return reward
 ```

-3. Wraps `run_agent_return_reward` function into a `run_and_submit` function, you can use the `run_and_submit_rewards` function in `areal.utils.proxy_utils` to do this.
+3. Wraps `run_agent_return_reward` function into a `run_and_submit` function, you can
+   use the `run_and_submit_rewards` function in `areal.utils.proxy_utils` to do this.
+
 ```python
 async def run_and_submit(data: dict):
     await run_and_submit_rewards(func=run_agent_return_reward, data=data)
@@ -50,5 +54,7 @@ agent_module_path: "examples.experimental.proxy.gsm8k_agent"

 ## The configuration file for the examples

-The `config.yaml` file is identical to `examples/multi-turn-math/gsm8k_grpo_mt.yaml` and can be used by any examples here.
-You may modify the configuration file to fit your needs, or override configuration values in the command line (see quick start above as an example).
+The `config.yaml` file is identical to `examples/multi-turn-math/gsm8k_grpo_mt.yaml` and
+can be used by any examples here. You may modify the configuration file to fit your
+needs, or override configuration values in the command line (see quick start above as an
+example).
diff --git a/examples/multi-turn-math/README.md b/examples/multi-turn-math/README.md
index e8078ff34..0218cbf03 100644
--- a/examples/multi-turn-math/README.md
+++ b/examples/multi-turn-math/README.md
@@ -13,6 +13,7 @@ python3 -m areal.launcher.ray examples/multi-turn-math/gsm8k_rl_mt.py \
 ```

 only the following config are added compared to the original `gsm8k_grpo.yaml` config:
+
 ```yaml
 export_style: concat
 agent_run_args:

PATCH

echo "Patch applied successfully."
