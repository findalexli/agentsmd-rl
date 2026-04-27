#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency: skip if the gold patch is already applied.
if [ -f .claude/skills/add-rollout-function/SKILL.md ] \
    && grep -q "Async RL-style rollout" .claude/skills/add-rollout-function/SKILL.md 2>/dev/null; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills b/.agents/skills
new file mode 120000
index 0000000000..454b8427cd
--- /dev/null
+++ b/.agents/skills
@@ -0,0 +1 @@
+../.claude/skills
\ No newline at end of file
diff --git a/.claude/skills/add-dynamic-filter/SKILL.md b/.claude/skills/add-dynamic-filter/SKILL.md
new file mode 100644
index 0000000000..2041394390
--- /dev/null
+++ b/.claude/skills/add-dynamic-filter/SKILL.md
@@ -0,0 +1,101 @@
+---
+name: add-dynamic-filter
+description: Guide for adding dynamic/filter hooks in slime rollout pipeline. Use when user wants sample-group selection during rollout, buffer filtering before training, or per-sample masking/processing hooks.
+---
+
+# Add Dynamic Filter
+
+Add filtering hooks in rollout and buffer stages while preserving sample-group contracts.
+
+## When to Use
+
+Use this skill when:
+
+- User asks to filter sample groups during dynamic sampling
+- User asks to customize buffer extraction strategy
+- User asks to mask/remove some rollout samples before training
+- User asks to process all generated samples for logging/analysis
+
+## Step-by-Step Guide
+
+### Step 1: Pick the Correct Hook
+
+- Dynamic sampling filter: `--dynamic-sampling-filter-path`
+- Buffer filter: `--buffer-filter-path`
+- Per-sample rollout filter: `--rollout-sample-filter-path`
+- All-samples post process: `--rollout-all-samples-process-path`
+
+### Step 2: Implement the Function Signature
+
+Dynamic sampling filter (called in `slime/rollout/sglang_rollout.py`):
+
+```python
+def filter_function(args, samples, **kwargs):
+    # return DynamicFilterOutput or bool
+```
+
+Preferred return type:
+
+```python
+from slime.rollout.filter_hub.base_types import DynamicFilterOutput
+
+return DynamicFilterOutput(keep=True, reason=None)
+```
+
+Buffer filter (called in `slime/rollout/data_source.py`):
+
+```python
+def buffer_filter(args, rollout_id, buffer, num_samples):
+    return selected_groups
+```
+
+Rollout sample filter:
+
+```python
+def rollout_sample_filter(args, samples):
+    # modify sample.remove_sample in-place where needed
+```
+
+All-samples process:
+
+```python
+def process_all_samples(args, all_samples, data_source):
+    ...
+```
+
+### Step 3: Preserve Group Structure
+
+- Keep `list[list[Sample]]` structure intact where required.
+- Do not flatten sample groups unless downstream path expects flattened samples.
+- For sample removal, prefer `sample.remove_sample=True` over deleting objects.
+
+### Step 4: Wire and Validate
+
+Example wiring:
+
+```bash
+--dynamic-sampling-filter-path slime.rollout.filter_hub.dynamic_sampling_filters.check_reward_nonzero_std
+--buffer-filter-path <module>.buffer_filter
+--rollout-sample-filter-path <module>.rollout_sample_filter
+--rollout-all-samples-process-path <module>.process_all_samples
+```
+
+### Step 5: Measure Side Effects
+
+- Check final sample count remains aligned with `rollout_batch_size` expectations.
+- Verify drop reasons are surfaced in rollout metrics when dynamic filter is used.
+- Validate training still receives valid loss masks/rewards after filtering.
+
+## Common Mistakes
+
+- Returning wrong container type for buffer filter
+- Dropping samples by deletion instead of mask flagging
+- Losing sample-group alignment in group-RM setup
+- Adding expensive logic in hot filtering paths
+
+## Reference Locations
+
+- Dynamic filter types: `slime/rollout/filter_hub/base_types.py`
+- Dynamic filter example: `slime/rollout/filter_hub/dynamic_sampling_filters.py`
+- Rollout generation hook points: `slime/rollout/sglang_rollout.py`
+- Buffer filter hook point: `slime/rollout/data_source.py`
diff --git a/.claude/skills/add-eval-dataset-config/SKILL.md b/.claude/skills/add-eval-dataset-config/SKILL.md
new file mode 100644
index 0000000000..f59360687f
--- /dev/null
+++ b/.claude/skills/add-eval-dataset-config/SKILL.md
@@ -0,0 +1,91 @@
+---
+name: add-eval-dataset-config
+description: Guide for adding and validating evaluation dataset configuration in slime. Use when user wants to configure eval datasets via --eval-config or --eval-prompt-data, add per-dataset overrides, or customize evaluation rollout behavior.
+---
+
+# Add Eval Dataset Config
+
+Configure evaluation datasets in slime with explicit dataset-level overrides and predictable runtime behavior.
+
+## When to Use
+
+Use this skill when:
+
+- User asks to add evaluation datasets for periodic eval
+- User asks to migrate from `--eval-prompt-data` to structured `--eval-config`
+- User asks for per-dataset eval overrides (sampling params, keys, rm_type, metadata)
+
+## Step-by-Step Guide
+
+### Step 1: Choose Config Entry Method
+
+Supported inputs:
+
+- Structured config file: `--eval-config <yaml>`
+- Legacy CLI pairs: `--eval-prompt-data <name1> <path1> <name2> <path2> ...`
+
+If `--eval-interval` is set, eval datasets must be configured.
+
+### Step 2: Build YAML with Required Fields
+
+Each dataset needs at least:
+
+- `name`
+- `path`
+
+Example:
+
+```yaml
+eval:
+  defaults:
+    n_samples_per_eval_prompt: 1
+    temperature: 0.7
+    top_p: 1.0
+  datasets:
+    - name: aime
+      path: /path/to/aime.jsonl
+      rm_type: math
+      input_key: prompt
+      label_key: answer
+      metadata_overrides:
+        split: test
+```
+
+### Step 3: Understand Override Priority
+
+`slime/utils/eval_config.py` resolves fields in this order:
+
+1. Dataset-level values in `eval.datasets[*]`
+2. `eval.defaults`
+3. CLI args fallback (for example eval_* or rollout_* fields)
+
+Common overridable fields include:
+
+- Runtime: `n_samples_per_eval_prompt`, `temperature`, `top_p`, `top_k`, `max_response_len`
+- Sample keys: `input_key`, `label_key`, `tool_key`, `metadata_key`
+- Extra: `rm_type`, `custom_generate_function_path`, `metadata_overrides`
+
+### Step 4: Wire Eval Function if Needed
+
+By default, eval uses `--eval-function-path` (defaults to rollout function path).
+Use a separate eval function when inference/eval behavior must differ from training rollout.
+
+### Step 5: Validate Parsing and Runtime
+
+- Start with config parsing sanity by running a short launch command.
+- Confirm dataset entries are loaded into `args.eval_datasets`.
+- Verify output keys match eval logging/metrics expectations.
+
+## Common Mistakes
+
+- Missing `name` in dataset entries
+- Odd-length `--eval-prompt-data` pairs
+- Setting `--eval-interval` without any eval dataset
+- Mixing reward dict outputs without `eval_reward_key` configuration
+
+## Reference Locations
+
+- Eval config model: `slime/utils/eval_config.py`
+- Eval config resolution: `slime/utils/arguments.py`
+- Eval rollout path: `slime/rollout/sglang_rollout.py`
+- Customization docs: `docs/en/get_started/customization.md`
diff --git a/.claude/skills/add-reward-function/SKILL.md b/.claude/skills/add-reward-function/SKILL.md
new file mode 100644
index 0000000000..f6ba3f9a79
--- /dev/null
+++ b/.claude/skills/add-reward-function/SKILL.md
@@ -0,0 +1,90 @@
+---
+name: add-reward-function
+description: Guide for adding a custom reward function in slime and wiring it through --custom-rm-path (and optional reward post-processing). Use when user wants new reward logic, remote/service reward integration, or task-specific reward shaping.
+---
+
+# Add Reward Function
+
+Implement custom reward logic and connect it to slime rollout/training safely.
+
+## When to Use
+
+Use this skill when:
+
+- User asks to add new reward computation logic
+- User asks to integrate an external reward service
+- User asks to customize reward normalization/post-processing
+
+## Step-by-Step Guide
+
+### Step 1: Choose Reward Mode
+
+Pick one of these:
+
+- Single-sample mode (`--group-rm` disabled): custom function gets one `Sample`
+- Group/batch mode (`--group-rm` enabled): custom function gets `list[Sample]`
+
+`slime.rollout.rm_hub.__init__.py` calls your function via `--custom-rm-path`.
+
+### Step 2: Create Reward Module
+
+Create `slime/rollout/rm_hub/<your_rm>.py`.
+
+Supported signatures:
+
+```python
+async def custom_rm(args, sample):
+    return float_reward_or_reward_dict
+```
+
+```python
+async def custom_rm(args, samples):
+    return list_of_rewards
+```
+
+If using group mode, return one reward per sample in input order.
+
+### Step 3: Keep Reward Type Consistent
+
+- Return scalar numeric rewards unless your pipeline explicitly uses keyed rewards.
+- If using reward dicts, ensure downstream `reward_key` / `eval_reward_key` is configured.
+- Keep exceptions explicit for invalid metadata instead of silently returning zeros.
+
+### Step 4: Optional Reward Post-Processing
+
+To customize normalization/shaping before advantage computation, add:
+
+```python
+def post_process_rewards(args, samples):
+    # return (raw_rewards, processed_rewards)
+    ...
+```
+
+Wire with:
+
+```bash
+--custom-reward-post-process-path <module>.post_process_rewards
+```
+
+This hook is consumed in `slime/ray/rollout.py`.
+
+### Step 5: Wire and Validate
+
+Use:
+
+```bash
+--custom-rm-path slime.rollout.rm_hub.<your_rm>.custom_rm
+```
+
+## Common Mistakes
+
+- Returning wrong output shape in group mode
+- Mixing scalar rewards and reward dicts without `reward_key` config
+- Doing blocking network calls without async handling
+- Forgetting to validate reward behavior on truncated/failed samples
+
+## Reference Locations
+
+- Reward dispatch: `slime/rollout/rm_hub/__init__.py`
+- Reward post-process hook: `slime/ray/rollout.py`
+- Customization docs: `docs/en/get_started/customization.md`
diff --git a/.claude/skills/add-rollout-function/SKILL.md b/.claude/skills/add-rollout-function/SKILL.md
new file mode 100644
index 0000000000..c8623a135b
--- /dev/null
+++ b/.claude/skills/add-rollout-function/SKILL.md
@@ -0,0 +1,108 @@
+---
+name: add-rollout-function
+description: Guide for adding a new rollout function in slime and wiring it through --rollout-function-path. Use when user wants to implement custom rollout data generation logic, custom train/eval rollout outputs, or migrate from the default sglang rollout path.
+---
+
+# Add Rollout Function
+
+Implement a custom rollout function and integrate it safely with slime training/eval flow.
+
+## When to Use
+
+Use this skill when:
+
+- User asks to add a new rollout task or rollout generation function
+- User asks to replace default `slime.rollout.sglang_rollout.generate_rollout`
+- User asks to customize train/eval data generation behavior
+
+## Step-by-Step Guide
+
+### Step 1: Choose the Right Starting Point
+
+Start from one of these references:
+
+- Async RL-style rollout: `slime/rollout/sglang_rollout.py`
+- Simple SFT-style rollout: `slime/rollout/sft_rollout.py`
+
+If the task needs engine-based async generation and rewards, use the sglang path as base.
+If the task is file/buffer-driven and simple, use sft path as base.
+
+### Step 2: Create the New Rollout Module
+
+Create a new file, for example: `slime/rollout/<your_rollout>.py`
+
+Required callable signature:
+
+```python
+def generate_rollout(args, rollout_id, data_source, evaluation=False) -> RolloutFnTrainOutput | RolloutFnEvalOutput:
+    ...
+```
+
+Return types are defined in `slime/rollout/base_types.py`.
+
+### Step 3: Implement Train and Eval Branches Explicitly
+
+- For training (`evaluation=False`), return `RolloutFnTrainOutput(samples=..., metrics=...)`
+- For evaluation (`evaluation=True`), return `RolloutFnEvalOutput(data=..., metrics=...)`
+
+Minimal skeleton:
+
+```python
+from slime.rollout.base_types import RolloutFnTrainOutput, RolloutFnEvalOutput
+
+
+def generate_rollout(args, rollout_id, data_source, evaluation=False):
+    if evaluation:
+        result = {
+            "custom_eval": {
+                "rewards": [],
+                "truncated": [],
+                "samples": [],
+            }
+        }
+        return RolloutFnEvalOutput(data=result)
+
+    groups = data_source.get_samples(args.rollout_batch_size)
+    # fill Sample fields needed by training: tokens/response_length/reward/status (+ loss_mask when needed)
+    return RolloutFnTrainOutput(samples=groups)
+```
+
+### Step 4: Keep Data Contract Compatible
+
+For each generated sample, ensure required training fields are populated consistently with your objective:
+
+- `tokens`
+- `response_length`
+- `reward` (or reward dict if your setup uses keyed rewards)
+- `status`
+
+If partial rollout or masking logic is involved, keep `loss_mask` semantics consistent with existing behavior.
+
+### Step 5: Wire Through Arguments
+
+Set your function path via CLI:
+
+```bash
+--rollout-function-path slime.rollout.<your_rollout>.generate_rollout
+```
+
+The default and signature expectation are documented in:
+
+- `slime/utils/arguments.py`
+- `docs/en/get_started/customization.md`
+
+## Common Mistakes
+
+- Returning raw Python lists/dicts with mismatched schema in custom path
+- Implementing only training branch and forgetting evaluation branch
+- Generating samples without required fields (`tokens`, `response_length`, `reward`, `status`)
+- Using blocking-heavy logic in high-frequency rollout paths without batching/concurrency control
+
+## Reference Locations
+
+- Default rollout: `slime/rollout/sglang_rollout.py`
+- Simple custom example: `slime/rollout/sft_rollout.py`
+- Output dataclasses: `slime/rollout/base_types.py`
+- Wiring/loading: `slime/ray/rollout.py`
+- Argument definition: `slime/utils/arguments.py`
+- Customization docs: `docs/en/get_started/customization.md`
diff --git a/.claude/skills/add-tests-and-ci/SKILL.md b/.claude/skills/add-tests-and-ci/SKILL.md
new file mode 100644
index 0000000000..ac5e514b01
--- /dev/null
+++ b/.claude/skills/add-tests-and-ci/SKILL.md
@@ -0,0 +1,71 @@
+---
+name: add-tests-and-ci
+description: Guide for adding or updating slime tests and CI wiring. Use when tasks require new test cases, CI registration, test matrix updates, or workflow template changes.
+---
+
+# Add Tests and CI
+
+Add reliable tests and integrate them with slime CI flow.
+
+## When to Use
+
+Use this skill when:
+
+- User asks to add tests for new behavior
+- User asks to fix or update existing tests in `tests/`
+- User asks to update CI workflow behavior
+- User asks how to run targeted checks before PR
+
+## Step-by-Step Guide
+
+### Step 1: Pick the Right Test Pattern
+
+- Follow existing naming: `tests/test_<feature>.py`
+- Start from nearest existing test file for your model/path
+- Keep test scope small and behavior-focused
+
+### Step 2: Keep CI Compatibility
+
+When creating CI-discoverable tests, ensure top-level constants and conventions match repository patterns (including `NUM_GPUS = <N>` where expected).
+
+### Step 3: Run Local Validation
+
+- Run the exact existing test files you changed, if any.
+- Run repository-wide checks only when they are already part of the task or workflow.
+- Avoid documenting placeholder test commands that may not exist in the current tree.
+
+### Step 4: Update Workflow Template Correctly
+
+For CI workflow changes:
+
+1. Edit `.github/workflows/pr-test.yml.j2`
+2. Regenerate workflows:
+
+```bash
+python .github/workflows/generate_github_workflows.py
+```
+
+3. Commit both template and generated workflow files
+
+### Step 5: Provide Verifiable PR Notes
+
+Include:
+
+- Which tests were added/changed
+- Exact commands executed
+- GPU assumptions for each test path
+- Why this coverage protects against regression
+
+## Common Mistakes
+
+- Editing generated workflow file only
+- Adding tests without following existing constants/conventions
+- Making tests too large or non-deterministic
+- Skipping local validation and relying only on remote CI
+
+## Reference Locations
+
+- Pytest config: `pyproject.toml`
+- Tests: `tests/`
+- CI template: `.github/workflows/pr-test.yml.j2`
+- CI guide: `docs/en/developer_guide/ci.md`
PATCH

echo "Gold patch applied successfully."
