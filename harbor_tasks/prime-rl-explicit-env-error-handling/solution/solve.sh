#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'has_error = state\["error"\] is not None' src/prime_rl/orchestrator/trajectories.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/configs/math_python/README.md b/configs/math_python/README.md
new file mode 100644
index 0000000000..e6ff710aba
--- /dev/null
+++ b/configs/math_python/README.md
@@ -0,0 +1,43 @@
+# math-python
+
+## Setup
+
+CLone `verifiers`
+
+```bash
+cd ~ && curl -sSL https://raw.githubusercontent.com/PrimeIntellect-ai/verifiers/main/scripts/install.sh | bash && cd -
+```
+
+Install the environment as local packages
+
+```bash
+uv pip install -e ~/verifiers/environments/math_python
+```
+
+This will automatically install the environment, and a pinned verifiers commit (`71006c`) which includes necessary changes to the PythonEnv.
+
+## Eval
+
+Get a quick vibe-check of the model
+
+```bash
+vllm serve Qwen/Qwen3-4B-Instruct-2507 --enable-auto-tool-choice --tool-call-parser hermes --max-model-len 8192
+```
+
+```bash
+uv run --no-sync vf-eval math-python -n 16 -r 1 -c -1 -v -m Qwen/Qwen3-4B-Instruct-2507 -b http://localhost:8000/v1 -a '{"dataset_name": "PrimeIntellect/Hendrycks-Math", "dataset_subset": "default"}' -t 512
+```
+
+## RL
+
+Again, make sure to have installed the environment as local packages from verifiers
+
+```bash
+uv pip install -e ~/verifiers/environments/math_python
+```
+
+Then, run RL in debug mode (small batch size, limited turns, 2 GPUs, etc.)
+
+```bash
+uv run --no-sync rl @ configs/math_python/math_python.toml --log.level debug
+```
\ No newline at end of file
diff --git a/configs/math_python/math_python.toml b/configs/math_python/math_python.toml
new file mode 100644
index 0000000000..3fa0360605
--- /dev/null
+++ b/configs/math_python/math_python.toml
@@ -0,0 +1,29 @@
+max_steps = 300
+
+[wandb]
+project = "math-python-debug"
+name = "math-python"
+
+[model]
+name = "Qwen/Qwen3-4B-Instruct-2507"
+
+[orchestrator]
+seq_len = 4096
+batch_size = 512
+rollouts_per_example = 16
+
+[orchestrator.sampling]
+max_tokens = 512
+
+[[orchestrator.env]]
+id = "math-python"
+
+[trainer] # Default trainer config
+
+[inference]
+api_server_count = 4
+
+[inference.model]
+enable_auto_tool_choice = true
+tool_call_parser = "hermes"
+max_model_len = 4096
\ No newline at end of file
diff --git a/pyproject.toml b/pyproject.toml
index 87f80906a7..8ef2ea72ef 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -70,7 +70,7 @@ prerelease = "allow"
 [tool.uv.sources]
 torch = { index = "pytorch-cu128" }
 reverse-text = { index = "primeintellect" }
-verifiers = { git = "https://github.com/PrimeIntellect-ai/verifiers.git", rev = "ca6aca7" }
+verifiers = { git = "https://github.com/PrimeIntellect-ai/verifiers.git", rev = "ca75d04" }
 dion = { git = "https://github.com/samsja/dion.git", rev = "main" }
 torchtitan = { git = "https://github.com/pytorch/torchtitan", rev = "a1fdd7e" }

diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index 1ae524d1b8..a7499649c8 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.py
@@ -55,7 +55,7 @@
     resolve_latest_ckpt_step,
     to_col_format,
 )
-from prime_rl.utils.vf import generate_batch, get_completion_len, get_is_truncated, get_prompt_len, get_seq_len
+from prime_rl.utils.vf import generate_batch, get_completion_len, get_prompt_len, get_seq_len


 @clean_exit
@@ -308,9 +308,10 @@ async def orchestrate(config: OrchestratorConfig):
         train_examples: list[TrainingSample] = []
         for train_rollout, advantage in zip(train_rollouts, advantages):
             train_example = make_train_example(train_rollout)
-            for te in train_example:
-                te.advantage = advantage
-            train_examples.extend(train_example)
+            if train_example is not None:
+                for te in train_example:
+                    te.advantage = advantage
+                train_examples.extend(train_example)
         logger.debug(
             f"Converted {len(train_rollouts)} training rollouts to {len(train_examples)} training examples using {config.trajectory_strategy} strategy"
         )
@@ -335,7 +336,11 @@ async def orchestrate(config: OrchestratorConfig):
                 "example_id": [rollout["example_id"] for rollout in train_rollouts],
                 "task": [rollout["task"] for rollout in train_rollouts],
                 "reward": [rollout["reward"] for rollout in train_rollouts],
-                "is_truncated": [get_is_truncated(rollout) for rollout in train_rollouts],
+                "is_truncated": [rollout["is_truncated"] for rollout in train_rollouts],
+                "error": [
+                    type(rollout["error"]).__name__ if rollout["error"] is not None else None
+                    for rollout in train_rollouts
+                ],
                 "completion_len": [get_completion_len(rollout) for rollout in train_rollouts],
                 "prompt_len": [get_prompt_len(rollout) for rollout in train_rollouts],
                 "seq_len": [get_seq_len(rollout) for rollout in train_rollouts],
@@ -409,6 +414,12 @@ async def orchestrate(config: OrchestratorConfig):
             "batch/solve_none": solve_none,
             "batch/solve_all": solve_all,
             "batch/effective_batch_size": effective_batch_size,
+            # Error metrics
+            "error/mean": (~results_df.error.isna()).mean(),
+            **{
+                f"error/{error}": error_rate
+                for error, error_rate in results_df.error.dropna().value_counts(normalize=True).items()
+            },
             # Env metrics
             **{f"metrics/{metric}": metrics_df[metric].mean() for metric in metrics_df.columns},
             # Time metrics

diff --git a/src/prime_rl/orchestrator/trajectories.py b/src/prime_rl/orchestrator/trajectories.py
index f0abbecda2..7caa5ef927 100644
--- a/src/prime_rl/orchestrator/trajectories.py
+++ b/src/prime_rl/orchestrator/trajectories.py
@@ -6,7 +6,7 @@
 from prime_rl.utils.logger import get_logger


-def interleave_rollout(state: vf.State) -> list[TrainingSample]:
+def interleave_rollout(state: vf.State) -> list[TrainingSample] | None:
     """
     Convert vf.State to a *single* trainable rollout by interleaving the trajectory.

@@ -16,14 +16,24 @@ def interleave_rollout(state: vf.State) -> list[TrainingSample]:
     """
     logger = get_logger()

-    # Initialize the rollout with prompt and completion from first trajectory step
     trajectory = state["trajectory"]
+    if len(trajectory) == 0:
+        logger.warning(f"No trajectory steps for example {state['example_id']}. Skipping rollout.")
+        return None
+
+    has_error = state["error"] is not None
+
+    # Initialize the rollout with prompt and completion from first trajectory step
     first_step = trajectory[0]
+    if has_error:
+        completion_mask = [False] * len(first_step["tokens"]["completion_mask"])
+    else:
+        completion_mask = [bool(i) for i in first_step["tokens"]["completion_mask"]]
     interleaved_rollout = TrainingSample(
         prompt_ids=deepcopy(first_step["tokens"]["prompt_ids"]),
         prompt_mask=[bool(i) for i in first_step["tokens"]["prompt_mask"]],
         completion_ids=deepcopy(first_step["tokens"]["completion_ids"]),
-        completion_mask=[bool(i) for i in first_step["tokens"]["completion_mask"]],
+        completion_mask=completion_mask,
         completion_logprobs=deepcopy(first_step["tokens"]["completion_logprobs"]),
         advantage=None,
     )
@@ -51,7 +61,10 @@ def interleave_rollout(state: vf.State) -> list[TrainingSample]:
         completion_ids = deepcopy(tokens["completion_ids"])
         completion_logprobs = deepcopy(tokens["completion_logprobs"])
         interleaved_rollout.completion_ids.extend(completion_ids)
-        interleaved_rollout.completion_mask.extend([True] * len(completion_ids))
+        if has_error:
+            interleaved_rollout.completion_mask.extend([False] * len(tokens["completion_mask"]))
+        else:
+            interleaved_rollout.completion_mask.extend([bool(i) for i in tokens["completion_mask"]])
         interleaved_rollout.completion_logprobs.extend(completion_logprobs)

         # New prefix is the current prompt and completion ids concatenated
@@ -60,17 +73,29 @@ def interleave_rollout(state: vf.State) -> list[TrainingSample]:
     return [interleaved_rollout]


-def branch_rollout(state: vf.State) -> list[TrainingSample]:
+def branch_rollout(state: vf.State) -> list[TrainingSample] | None:
     """Convert vf.State to *multiple* trainable rollouts using branching trajectories strategy."""
+    logger = get_logger()
+
     rollouts = []
+    trajectory = state["trajectory"]
+    if len(trajectory) == 0:
+        logger.warning(f"No trajectory steps for example {state['example_id']}. Skipping rollout.")
+        return None
+
+    has_error = state["error"] is not None
     for step in state["trajectory"]:
         assert "tokens" in step
         tokens = step["tokens"]
+        if has_error:
+            completion_mask = [False] * len(tokens["completion_mask"])
+        else:
+            completion_mask = [bool(i) for i in tokens["completion_mask"]]
         rollout = TrainingSample(
             prompt_ids=deepcopy(tokens["prompt_ids"]),
             prompt_mask=[bool(i) for i in tokens["prompt_mask"]],
             completion_ids=deepcopy(tokens["completion_ids"]),
-            completion_mask=[bool(i) for i in tokens["completion_mask"]],
+            completion_mask=completion_mask,
             completion_logprobs=deepcopy(tokens["completion_logprobs"]),
             advantage=None,
         )

diff --git a/tests/unit/orchestrator/test_trajectories.py b/tests/unit/orchestrator/test_trajectories.py
index 39f237a8fd..4f44d88c10 100644
--- a/tests/unit/orchestrator/test_trajectories.py
+++ b/tests/unit/orchestrator/test_trajectories.py
@@ -28,6 +28,7 @@ def single_step_trajectory_state():
                 extras={},
             )
         ],
+        error=None,
     )
     return state

@@ -75,6 +76,7 @@ def multi_step_trajectory_state():
                 extras={},
             ),
         ],
+        error=None,
     )
     return state

@@ -126,6 +128,7 @@ def multi_step_trajectory_with_tool_calls():
         advantage=None,
         stop_condition=None,
         metrics={"has_error": 0.0, "tool_calls": 1.0},
+        error=None,
     )
     return state

diff --git a/uv.lock b/uv.lock
index a59d667d47..0943dbd4f5 100644
--- a/uv.lock
+++ b/uv.lock
@@ -2294,7 +2294,7 @@ requires-dist = [
     { name = "torchtitan", git = "https://github.com/pytorch/torchtitan?rev=a1fdd7e" },
     { name = "transformers", specifier = ">=4.56.0" },
     { name = "uvloop", specifier = ">=0.21.0" },
-    { name = "verifiers", git = "https://github.com/PrimeIntellect-ai/verifiers.git?rev=ca6aca7" },
+    { name = "verifiers", git = "https://github.com/PrimeIntellect-ai/verifiers.git?rev=ca75d04" },
     { name = "vllm", specifier = "==0.10.2" },
     { name = "wandb", specifier = ">=0.20.1" },
 ]
@@ -3640,8 +3640,8 @@ wheels = [

 [[package]]
 name = "verifiers"
-version = "0.1.8.post1"
-source = { git = "https://github.com/PrimeIntellect-ai/verifiers.git?rev=ca6aca7#ca6aca7389a09df5305a8751b4edf34ab4e06f91" }
+version = "0.1.8.post2"
+source = { git = "https://github.com/PrimeIntellect-ai/verifiers.git?rev=ca75d04#ca75d04002c8e8d4eb766720ecd19e91abc02f20" }
 dependencies = [
     { name = "datasets" },
     { name = "jinja2" },

PATCH

echo "Patch applied successfully."
