#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tinker-cookbook

# Idempotency guard
if grep -qF "Beyond saving and loading during training, you can manage checkpoints via the RE" ".claude/skills/checkpoints/SKILL.md" && grep -qF "description: Guide for training outputs, metrics logging, logtree reports, traci" ".claude/skills/logging/SKILL.md" && grep -qF "**Scope:** Raw Tinker Python SDK APIs \u2014 ServiceClient, TrainingClient, SamplingC" ".claude/skills/manage-skills/SKILL.md" && grep -qF "description: Guide for the Tinker CLI \u2014 managing training runs, checkpoints, dow" ".claude/skills/tinker-cli/SKILL.md" && grep -qF "description: Guide for using the Tinker Python SDK APIs \u2014 ServiceClient, Trainin" ".claude/skills/tinker-sdk/SKILL.md" && grep -qF "description: Reference for Tinker SDK types \u2014 Datum, ModelInput, TensorData, Sam" ".claude/skills/tinker-types/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/checkpoints/SKILL.md b/.claude/skills/checkpoints/SKILL.md
@@ -101,9 +101,39 @@ if config.load_checkpoint_path:
 
 Set `behavior_if_log_dir_exists=resume` to continue from the last checkpoint in an existing log directory.
 
+## Managing checkpoints (REST API / CLI)
+
+Beyond saving and loading during training, you can manage checkpoints via the REST API or CLI. See `/tinker-sdk` for RestClient details and `/tinker-cli` for CLI commands.
+
+```python
+from tinker import ServiceClient
+rest = ServiceClient().create_rest_client()
+
+# List all your checkpoints
+checkpoints = rest.list_user_checkpoints(limit=100)
+
+# Publish a checkpoint (make it publicly accessible)
+rest.publish_checkpoint_from_tinker_path("tinker://...")
+
+# Set TTL (auto-delete after N seconds)
+rest.set_checkpoint_ttl_from_tinker_path("tinker://...", ttl_seconds=86400)
+
+# Delete a checkpoint
+rest.delete_checkpoint_from_tinker_path("tinker://...")
+```
+
+Or via CLI:
+```bash
+tinker checkpoint list
+tinker checkpoint publish <TINKER_PATH>
+tinker checkpoint set-ttl <TINKER_PATH> --ttl 86400
+tinker checkpoint delete <TINKER_PATH>
+```
+
 ## Common pitfalls
 - Use `save_state` for resumable checkpoints, `save_weights_for_sampler` for sampling/export
 - `get_last_checkpoint()` returns `None` if no matching checkpoint exists — always check
 - Checkpoint paths start with `tinker://` — they reference remote storage, not local files
 - Set `ttl_seconds` on intermediate checkpoints to avoid accumulating old weights
 - For RLHF pipelines, the SFT stage saves `state_path` (for RL init) and the RM stage saves `sampler_path` (for reward scoring)
+- `delete` is permanent — there is no undo
diff --git a/.claude/skills/logging/SKILL.md b/.claude/skills/logging/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: logging
-description: Guide for training outputs, metrics logging, logtree reports, and debugging training runs. Use when the user asks about training logs, metrics, debugging, analyzing training runs, or understanding training output files.
+description: Guide for training outputs, metrics logging, logtree reports, tracing/profiling, and debugging training runs. Use when the user asks about training logs, metrics, debugging, tracing, profiling, timing, Gantt charts, or understanding training output files.
 ---
 
 # Logging & Debugging
@@ -12,6 +12,7 @@ Every training run writes structured outputs to `log_path`. This skill covers wh
 - `docs/rl/rl-logging.mdx` — Complete file reference for RL training outputs
 - `tinker_cookbook/utils/ml_log.py` — Metrics logging API
 - `tinker_cookbook/utils/logtree.py` — Logtree (structured rollout transcripts)
+- `tinker_cookbook/utils/trace.py` — Tracing/profiling (`@scope`, `trace_iteration`, Gantt charts)
 
 ## Output files
 
@@ -27,6 +28,9 @@ Each training run writes to its `log_path` directory:
 | `train_iteration_NNNNNN_logtree.json` | JSON | Machine-readable rollout transcripts |
 | `train_iteration_NNNNNN_rollout_summaries.jsonl` | JSONL | Per-trajectory rewards and metrics |
 | `eval_<name>_iteration_NNNNNN.*` | mixed | Same formats for eval rollouts |
+| `timing_spans.jsonl` | JSONL | Per-iteration span timing data (from `trace_iteration`) |
+| `trace_events.jsonl` | JSONL | Perfetto/Chrome Trace format events (from `trace_init`) |
+| `gantt_NNNNNN.html` | HTML | Plotly Gantt chart of span timeline (optional) |
 
 Iteration numbers are zero-padded to 6 digits.
 
@@ -55,8 +59,10 @@ df.plot(x="progress/batch", y="env/all/reward/total")
 - `optim/lr` — current learning rate
 - `ac_tokens_per_turn` — mean generated tokens per turn
 
-**Timing:**
-- `time/...` — wall-clock timings for different stages
+**Timing** (from `trace_iteration`):
+- `time/total` — iteration wall-clock duration
+- `time/<name>` — single-call duration (e.g., `time/train_step`)
+- `time/<name>:total`, `time/<name>:count`, `time/<name>:mean`, `time/<name>:max` — aggregates for functions called multiple times (e.g., `time/sample_async:total`)
 
 ## Analyzing rollouts
 
@@ -76,34 +82,11 @@ for traj in trajectories:
 
 ### Logtree JSON (full transcripts)
 
-Contains full text of prompts, model responses, grading details:
-
-```python
-import json
-
-def find_conversations(node):
-    results = []
-    if isinstance(node, dict):
-        if node.get("data", {}).get("type") == "conversation":
-            results.append(node["data"])
-        for child in node.get("children", []):
-            if isinstance(child, dict):
-                results.extend(find_conversations(child))
-    return results
-
-with open("train_iteration_000010_logtree.json") as f:
-    trace = json.load(f)
-
-for conv in find_conversations(trace["root"]):
-    for msg in conv["messages"]:
-        print(f"{msg['role']}: {msg['content'][:100]}")
-```
+Contains full text of prompts, model responses, grading details. Walk the tree recursively looking for nodes with `data.type == "conversation"` to extract conversations. See `docs/rl/rl-logging.mdx` for the full schema.
 
 ### HTML reports
 
-Open `train_iteration_NNNNNN.html` in a browser for a human-readable view of rollouts with collapsible sections.
-
-`num_groups_to_log` (default: 4) controls how many trajectory groups get detailed logging.
+Open `train_iteration_NNNNNN.html` in a browser for a human-readable view of rollouts with collapsible sections. `num_groups_to_log` (default: 4) controls how many trajectory groups get detailed logging.
 
 ## Logging in your own code
 
@@ -141,6 +124,65 @@ config = train.Config(
 )
 ```
 
+## Tracing & profiling
+
+The `tinker_cookbook/utils/trace` module provides per-iteration profiling across all training modules (RL, SL, DPO, distillation).
+
+### Core API
+
+```python
+from tinker_cookbook.utils import trace
+
+# Initialize Perfetto trace collector (optional — writes trace_events.jsonl)
+trace.trace_init()
+
+# In training loop — collect per-iteration timing
+for i_batch in range(n_batches):
+    with trace.trace_iteration(step=i_batch) as window:
+        # All @scope-decorated calls are automatically recorded
+        await gather_rollouts(...)
+        await train_step(...)
+
+    # Get timing metrics for this iteration
+    metrics.update(window.get_timing_metrics())
+
+    # Persist span data for post-hoc analysis
+    window.write_spans_jsonl(log_path / "timing_spans.jsonl", step=i_batch)
+
+    # Optional: Gantt chart visualization (requires plotly)
+    trace.save_gantt_chart_html(window, i_batch, log_path / f"gantt_{i_batch}.html")
+```
+
+### Instrumenting your code
+
+```python
+from tinker_cookbook.utils import trace
+
+# Decorator — automatically traces function calls
+@trace.scope
+async def my_training_step(tc, batch):
+    result = await tc.forward_backward_async(data=batch, loss_fn="cross_entropy")
+    return result
+
+# Inline span — for timing a code block without a dedicated function
+async with trace.scope_span("data_prep"):
+    batch = prepare_next_batch(...)
+
+# Sync variant
+with trace.scope_span_sync("data_prep"):
+    batch = prepare_next_batch(...)
+```
+
+`@scope` and `scope_span` are no-ops when called outside `trace_iteration` — safe to leave in production.
+
+### Viewing Perfetto traces
+
+```bash
+# Convert JSONL to JSON for visualization
+uv run python -m tinker_cookbook.utils.trace trace_events.jsonl trace.json
+# Open trace.json in chrome://tracing or https://ui.perfetto.dev/
+```
+
 ## Debugging tips
 
 1. **Training not improving**: Check `metrics.jsonl` — is loss decreasing? Are rewards increasing?
diff --git a/.claude/skills/manage-skills/SKILL.md b/.claude/skills/manage-skills/SKILL.md
@@ -18,9 +18,9 @@ All skills in `.claude/skills/` are organized into 5 layers:
 **Auto-invocation:** Yes — triggers when users ask about setup, models, hyperparameters, or debugging.
 **Key principle:** These inform all other layers. Reference `docs/`, `README.md`, `tinker_cookbook/hyperparam_utils.py`.
 
-### Layer 1: Tinker SDK (`tinker-sdk`, `tinker-types`)
-**Scope:** Raw Tinker Python SDK APIs — TrainingClient, SamplingClient, forward_backward, optim_step, sampling, types.
-**Auto-invocation:** Yes — triggers when users ask about Tinker API basics.
+### Layer 1: Tinker SDK (`tinker-sdk`, `tinker-types`, `tinker-cli`)
+**Scope:** Raw Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, types, errors, and CLI commands.
+**Auto-invocation:** Yes — triggers when users ask about Tinker API basics or CLI usage.
 **Key principle:** Reference `docs/api-reference/` for authoritative API docs.
 
 ### Layer 2: Cookbook Primitives (`renderers`, `environments`, `weights`, `completers`, `checkpoints`, `evals`, `datasets`)
@@ -120,8 +120,9 @@ When auditing, check each skill for:
 │   ├── hyperparams/         # LR formulas, batch size, LoRA rank
 │   └── logging/             # Training outputs, metrics, debugging
 ├── Layer 1: SDK
-│   ├── tinker-sdk/          # TrainingClient, SamplingClient APIs
-│   └── tinker-types/        # Datum, ModelInput, TensorData, SamplingParams
+│   ├── tinker-sdk/          # ServiceClient, TrainingClient, SamplingClient, RestClient APIs
+│   ├── tinker-types/        # Datum, ModelInput, TensorData, response types, error types
+│   └── tinker-cli/          # tinker CLI: run/checkpoint management, download, publish
 ├── Layer 2: Primitives
 │   ├── renderers/           # Renderer setup, TrainOnWhat, vision
 │   ├── environments/        # Env, EnvGroupBuilder, custom RL envs
diff --git a/.claude/skills/tinker-cli/SKILL.md b/.claude/skills/tinker-cli/SKILL.md
@@ -0,0 +1,149 @@
+---
+name: tinker-cli
+description: Guide for the Tinker CLI — managing training runs, checkpoints, downloading weights, and publishing to HuggingFace. Use when the user asks about CLI commands, listing runs, managing checkpoints from the terminal, or uploading to HF Hub.
+---
+
+# Tinker CLI
+
+The `tinker` CLI is installed with the Tinker Python SDK. It provides commands for managing training runs and checkpoints from the terminal.
+
+Requires `TINKER_API_KEY` environment variable to be set.
+
+## Global options
+
+```bash
+tinker --format table   # Rich table output (default)
+tinker --format json    # JSON output (for scripting)
+```
+
+## Training runs
+
+```bash
+# List recent training runs
+tinker run list
+tinker run list --limit 50
+
+# Show details for a specific run
+tinker run info <RUN_ID>
+
+# Custom columns
+tinker run list --columns id,model,lora,updated,status,checkpoint
+```
+
+Available columns: `id`, `model`, `owner`, `lora`, `updated`, `status`, `checkpoint`, `checkpoint_time`.
+
+## Checkpoints
+
+### List and inspect
+
+```bash
+# List checkpoints for a specific run
+tinker checkpoint list --run-id <RUN_ID>
+
+# List all your checkpoints across runs
+tinker checkpoint list
+tinker checkpoint list --limit 50
+
+# Show checkpoint details
+tinker checkpoint info <TINKER_PATH>
+```
+
+### Download
+
+```bash
+# Download and extract a checkpoint
+tinker checkpoint download <TINKER_PATH>
+tinker checkpoint download <TINKER_PATH> --output ./my-adapter
+tinker checkpoint download <TINKER_PATH> --force  # Overwrite existing
+```
+
+### Visibility
+
+```bash
+# Make a checkpoint publicly accessible
+tinker checkpoint publish <TINKER_PATH>
+
+# Make a checkpoint private
+tinker checkpoint unpublish <TINKER_PATH>
+```
+
+### TTL (expiration)
+
+```bash
+# Set checkpoint to expire in 24 hours
+tinker checkpoint set-ttl <TINKER_PATH> --ttl 86400
+
+# Remove expiration (keep indefinitely)
+tinker checkpoint set-ttl <TINKER_PATH> --remove
+```
+
+### Delete
+
+```bash
+# Delete checkpoints (with confirmation prompt)
+tinker checkpoint delete <TINKER_PATH>
+
+# Delete without confirmation
+tinker checkpoint delete <TINKER_PATH> -y
+
+# Delete multiple
+tinker checkpoint delete <PATH1> <PATH2> <PATH3>
+```
+
+### Upload to HuggingFace Hub
+
+```bash
+# Push checkpoint to HuggingFace
+tinker checkpoint push-hf <TINKER_PATH> --repo user/my-model
+
+# Push as public repo
+tinker checkpoint push-hf <TINKER_PATH> --repo user/my-model --public
+
+# Advanced options
+tinker checkpoint push-hf <TINKER_PATH> \
+    --repo user/my-model \
+    --revision main \
+    --commit-message "Upload fine-tuned model" \
+    --create-pr \
+    --no-model-card
+```
+
+Options: `--repo`, `--public`, `--revision`, `--commit-message`, `--create-pr`, `--allow-pattern`, `--ignore-pattern`, `--no-model-card`.
+
+## Version
+
+```bash
+tinker version   # e.g. "tinker 0.15.0"
+```
+
+## Common patterns
+
+### Script-friendly output
+```bash
+# Get checkpoint paths as JSON for scripting
+tinker checkpoint list --format json | jq '.[].tinker_path'
+
+# Get run IDs
+tinker run list --format json | jq '.[].id'
+```
+
+### Typical workflow
+```bash
+# 1. Find your training run
+tinker run list
+
+# 2. List checkpoints for that run
+tinker checkpoint list --run-id <RUN_ID>
+
+# 3. Download the final checkpoint
+tinker checkpoint download tinker://<RUN_ID>/sampler_weights/final -o ./adapter
+
+# 4. Or push directly to HuggingFace
+tinker checkpoint push-hf tinker://<RUN_ID>/sampler_weights/final --repo user/my-model
+```
+
+## Common pitfalls
+- `TINKER_API_KEY` must be set — the CLI reads it from the environment
+- Checkpoint paths use the format `tinker://<run-id>/<type>/<checkpoint-id>`
+- `push-hf` uploads the raw checkpoint — for merged HF models, use `weights.build_hf_model()` in Python first (see `/weights` skill)
+- `delete` is permanent and irreversible — use `-y` flag carefully
diff --git a/.claude/skills/tinker-sdk/SKILL.md b/.claude/skills/tinker-sdk/SKILL.md
@@ -1,63 +1,102 @@
 ---
 name: tinker-sdk
-description: Guide for using the Tinker Python SDK APIs — TrainingClient, SamplingClient, forward_backward, optim_step, sampling, and async patterns. Use when the user asks about Tinker API basics, how to call training/sampling, or how the SDK works.
+description: Guide for using the Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, forward_backward, optim_step, sampling, and async patterns. Use when the user asks about Tinker API basics, how to call training/sampling, or how the SDK works.
 ---
 
 # Tinker Python SDK
 
 Help the user understand and use the core Tinker SDK APIs.
 
-## Overview
-
-The Tinker SDK provides two main clients:
-- **TrainingClient** — runs forward/backward passes, optimizer steps, checkpointing
-- **SamplingClient** — generates text from a model
-
-Both run on remote GPU workers. Your code runs on a CPU machine and calls the SDK over the network.
-
 ## Reference docs
 
 Read these for authoritative API documentation:
+- `docs/api-reference/serviceclient.md` — ServiceClient API
 - `docs/api-reference/trainingclient.md` — TrainingClient API
 - `docs/api-reference/samplingclient.md` — SamplingClient API
+- `docs/api-reference/restclient.md` — RestClient API
 - `docs/api-reference/types.md` — All SDK types
 - `docs/training-sampling.mdx` — Starter walkthrough
 - `docs/async.mdx` — Sync/async patterns, futures
 - `docs/losses.mdx` — Loss functions
 - `docs/under-the-hood.mdx` — Clock cycles, worker pools
 
-## TrainingClient
+## ServiceClient (entry point)
+
+`ServiceClient` is the main entry point. All other clients are created from it.
 
 ```python
-from tinker import TrainingClient
+from tinker import ServiceClient
+
+svc = ServiceClient(user_metadata={"experiment": "v1"}, project_id="my-project")
+
+# Create a new LoRA training client
+tc = svc.create_lora_training_client(
+    base_model="Qwen/Qwen3-8B",
+    rank=32,
+    seed=None,
+    train_mlp=True,
+    train_attn=True,
+    train_unembed=True,
+)
+
+# Resume from a training checkpoint
+tc = svc.create_training_client_from_state(path="tinker://...")              # weights only
+tc = svc.create_training_client_from_state_with_optimizer(path="tinker://...") # weights + optimizer
 
-tc = TrainingClient(model_name="meta-llama/Llama-3.1-8B")
+# Create a sampling client
+sc = svc.create_sampling_client(model_path="tinker://...", base_model=None, retry_config=None)
+
+# Create a REST client for checkpoint/run management
+rest = svc.create_rest_client()
+
+# Query available models
+caps = svc.get_server_capabilities()  # returns GetServerCapabilitiesResponse
+```
+
+All creation methods have `_async` variants.
+
+## TrainingClient
 
-# Forward/backward pass
+```python
+# Forward/backward pass (compute loss + gradients)
 result = tc.forward_backward(data=[datum1, datum2], loss_fn="cross_entropy")
 
+# Forward-only pass (compute loss, no gradients — useful for eval)
+result = tc.forward(data=[datum1, datum2], loss_fn="cross_entropy")
+
+# Custom loss function
+result = tc.forward_backward_custom(data=[datum1, datum2], loss_fn=my_custom_loss_fn)
+
 # Optimizer step
 tc.optim_step(adam_params=AdamParams(learning_rate=2e-4))
 
 # Checkpointing
-tc.save_state(name="step_100")                        # Full state (resumable)
-tc.save_weights_for_sampler(name="step_100_sampler")   # Sampler-only weights
+tc.save_state(name="step_100", ttl_seconds=None)                # Full state (resumable)
+tc.save_weights_for_sampler(name="step_100_sampler", ttl_seconds=None)  # Sampler-only
+
+# Save + get SamplingClient in one call
+sc = tc.save_weights_and_get_sampling_client(name="step_100")
 
 # Load checkpoint
 tc.load_state(path="tinker://...")
+tc.load_state_with_optimizer(path="tinker://...")
+
+# Metadata
+info = tc.get_info()          # GetInfoResponse (model name, LoRA rank, tokenizer)
+tokenizer = tc.get_tokenizer()  # HuggingFace tokenizer
 ```
 
-### Key methods
-- `forward_backward(data, loss_fn, loss_fn_config)` — Compute loss and gradients
-- `optim_step(adam_params)` — Apply gradients
-- `save_state(name, ttl_seconds)` — Save full state (weights + optimizer) for resumption
-- `save_weights_for_sampler(name, ttl_seconds)` — Save weights for sampling
-- `save_weights_and_get_sampling_client(name)` — Save + create SamplingClient in one call
-- `load_state(path)` / `load_state_with_optimizer(path)` — Resume from checkpoint
-- `get_tokenizer()` — Get the model's tokenizer
-- `get_info()` — Model metadata
+### Loss functions
+- `"cross_entropy"` — Standard SL loss
+- `"importance_sampling"` — On-policy RL (default for GRPO)
+- `"ppo"` — Proximal Policy Optimization
+- `"cispo"` — Conservative Importance Sampling PPO
+- `"dro"` — Distributionally Robust Optimization
+
+See `docs/losses.mdx` for details and `loss_fn_config` parameters.
 
 ### Async variants
+
 All methods have `_async` variants that return `APIFuture`:
 ```python
 fb_future = tc.forward_backward_async(data=data, loss_fn="cross_entropy")
@@ -67,67 +106,76 @@ fb_result = fb_future.result()
 optim_result = optim_future.result()
 ```
 
-**Key pattern:** Submit forward_backward_async and optim_step_async back-to-back before awaiting — this overlaps GPU computation with data preparation.
-
-### Loss functions
-- `"cross_entropy"` — Standard SL loss
-- `"importance_sampling"` — On-policy RL (default for GRPO)
-- `"ppo"` — Proximal Policy Optimization
-- `"cispo"` — Conservative Importance Sampling PPO
-- `"dro"` — Distributionally Robust Optimization
-- `"dpo"` — Direct Preference Optimization
-- `"forward_backward_custom"` — Custom loss via CustomLossFnV1
-
-See `docs/losses.mdx` for details and `loss_fn_config` parameters.
+**Key pattern:** Submit `forward_backward_async` and `optim_step_async` back-to-back before awaiting — this overlaps GPU computation with data preparation.
 
 ## SamplingClient
 
 ```python
-from tinker import SamplingClient, SamplingParams
+from tinker import SamplingParams
 
 sc = tc.save_weights_and_get_sampling_client(name="step_100")
-# OR
-sc = SamplingClient(model_path="tinker://...")
 
 response = sc.sample(
     prompt=model_input,
     num_samples=4,
     sampling_params=SamplingParams(max_tokens=256, temperature=1.0),
+    include_prompt_logprobs=False,   # Set True to get per-token prompt logprobs
+    topk_prompt_logprobs=0,          # Top-K logprobs per prompt token (0 = disabled)
 )
 
 for seq in response.sequences:
     print(seq.tokens, seq.logprobs, seq.stop_reason)
+
+# Get logprobs for existing tokens (no generation)
+logprobs_response = sc.compute_logprobs(prompt=model_input)
+
+# Metadata
+base_model = sc.get_base_model()    # Base model name string
+tokenizer = sc.get_tokenizer()      # HuggingFace tokenizer
 ```
 
-### Key methods
-- `sample(prompt, num_samples, sampling_params)` — Generate completions
-- `compute_logprobs(prompt)` — Get logprobs for existing tokens
-- `get_tokenizer()` — Get the model's tokenizer
+SamplingClient is picklable for multiprocessing use.
 
 **Important:** Always create a **new** SamplingClient after saving weights. A stale client points at old weights.
 
-## Common patterns
+## RestClient
+
+For managing training runs and checkpoints. See also the `/tinker-cli` skill for CLI equivalents.
 
-### Pipelined training loop
 ```python
-fb_future = tc.forward_backward_async(data=batch, loss_fn="cross_entropy")
-# Prepare next batch while GPU works...
-next_batch = prepare_batch(...)
-fb_result = fb_future.result()
+rest = svc.create_rest_client()
 
-optim_future = tc.optim_step_async(adam_params=adam_params)
-# Prepare more data...
-optim_result = optim_future.result()
-```
+# Training runs
+runs = rest.list_training_runs(limit=20, offset=0, access_scope="owned")
+run = rest.get_training_run(training_run_id="...")
+run = rest.get_training_run_by_tinker_path(tinker_path="tinker://...")
 
-### Save and sample
-```python
-sc = tc.save_weights_and_get_sampling_client(name=f"step_{step}")
-response = sc.sample(prompt=prompt, num_samples=4, sampling_params=params)
+# Checkpoints
+checkpoints = rest.list_checkpoints(training_run_id="...")
+all_checkpoints = rest.list_user_checkpoints(limit=100, offset=0)
+rest.delete_checkpoint(training_run_id="...", checkpoint_id="...")
+rest.delete_checkpoint_from_tinker_path(tinker_path="tinker://...")
+
+# Checkpoint visibility
+rest.publish_checkpoint_from_tinker_path(tinker_path="tinker://...")    # Make public
+rest.unpublish_checkpoint_from_tinker_path(tinker_path="tinker://...")  # Make private
+
+# Checkpoint TTL
+rest.set_checkpoint_ttl_from_tinker_path(tinker_path="tinker://...", ttl_seconds=86400)
+
+# Download URL
+url_resp = rest.get_checkpoint_archive_url_from_tinker_path(tinker_path="tinker://...")
+
+# Checkpoint metadata
+info = rest.get_weights_info_by_tinker_path(tinker_path="tinker://...")
 ```
 
+All RestClient methods have `_async` variants.
+
 ## Common pitfalls
+- **Use ServiceClient** to create clients — `TrainingClient` and `SamplingClient` cannot be constructed directly
 - Always await futures before submitting new forward_backward calls
-- Submit forward_backward_async + optim_step_async back-to-back before awaiting
+- Submit `forward_backward_async` + `optim_step_async` back-to-back before awaiting
 - Create a **new** SamplingClient after saving weights (sampler desync)
 - Use `save_state` for resumable checkpoints, `save_weights_for_sampler` for sampling-only
+- `forward()` computes loss without gradients — use for eval, not training
diff --git a/.claude/skills/tinker-types/SKILL.md b/.claude/skills/tinker-types/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: tinker-types
-description: Reference for Tinker SDK types — Datum, ModelInput, TensorData, SamplingParams, and helper functions for constructing them. Use when the user needs to build training data, construct model inputs, or understand the type hierarchy.
+description: Reference for Tinker SDK types — Datum, ModelInput, TensorData, SamplingParams, response types, error types, and helper functions. Use when the user needs to build training data, construct model inputs, understand response objects, or handle errors.
 ---
 
 # Tinker SDK Types
@@ -11,8 +11,9 @@ Quick reference for the core types used throughout the Tinker SDK and cookbook.
 
 Read `docs/api-reference/types.md` for the complete type reference.
 
-## Type hierarchy
+## Core data types
 
+### Type hierarchy
 ```
 Datum
 ├── model_input: ModelInput (list of chunks)
@@ -22,119 +23,161 @@ Datum
     └── TensorData (numpy/torch wrapper)
 ```
 
-## ModelInput
-
-A sequence of chunks representing the model's input (tokens + optional images).
-
+### ModelInput
 ```python
-from tinker.types import ModelInput
-
-# From token list
-mi = ModelInput.from_ints([1, 2, 3, 4, 5])
-
-# Get tokens back
-tokens = mi.to_ints()
-
-# Length
-length = mi.length()
-
-# Append
-mi2 = mi.append(another_chunk)
-
-# Empty
-mi_empty = ModelInput.empty()
+from tinker import ModelInput
+
+mi = ModelInput.from_ints([1, 2, 3, 4, 5])  # From token list
+tokens = mi.to_ints()                        # Back to list
+length = mi.length                           # Token count (property)
+mi2 = mi.append(chunk)                       # Append a chunk
+mi3 = mi.append_int(42)                      # Append a single token
+mi_empty = ModelInput.empty()                # Empty input
 ```
 
-## TensorData
-
-Wrapper for numpy arrays or torch tensors with shape info.
-
+### TensorData
 ```python
-from tinker.types import TensorData
-import numpy as np
-
-# From numpy
-td = TensorData.from_numpy(np.array([1.0, 0.0, 1.0, 0.0]))
-
-# From torch
-import torch
-td = TensorData.from_torch(torch.tensor([1.0, 0.0, 1.0, 0.0]))
-
-# Convert back
-arr = td.to_numpy()
-tensor = td.to_torch()
+from tinker import TensorData
+
+td = TensorData.from_numpy(np.array([1.0, 0.0, 1.0]))  # From numpy
+td = TensorData.from_torch(torch.tensor([1.0, 0.0]))    # From torch
+arr = td.to_numpy()                                       # Back to numpy
+tensor = td.to_torch()                                    # Back to torch
+lst = td.tolist()                                         # Back to list
+# Fields: data (flat list), dtype ("int64"|"float32"), shape (optional)
 ```
 
-## Datum
-
-A single training sample: model input + loss function inputs.
-
+### Datum
 ```python
-from tinker.types import Datum, ModelInput, TensorData
+from tinker import Datum, ModelInput, TensorData
 
 datum = Datum(
     model_input=ModelInput.from_ints(tokens),
-    loss_fn_inputs={
-        "weights": TensorData.from_numpy(weights_array),
-    },
+    loss_fn_inputs={"weights": TensorData.from_numpy(weights_array)},
 )
 ```
 
-## SamplingParams
-
-Controls text generation behavior.
+## Configuration types
 
+### SamplingParams
 ```python
-from tinker.types import SamplingParams
+from tinker import SamplingParams
 
 params = SamplingParams(
-    max_tokens=256,
-    temperature=1.0,
-    top_k=50,
-    top_p=0.95,
-    stop=["<|eot_id|>"],  # Stop sequences (strings or token IDs)
-    seed=42,
+    max_tokens=256,        # Max generation length
+    temperature=1.0,       # Sampling temperature
+    top_k=50,              # Top-K sampling (-1 = no limit)
+    top_p=0.95,            # Nucleus sampling
+    stop=["<|eot_id|>"],   # Stop sequences (strings or token IDs)
+    seed=42,               # Reproducible seed
 )
 ```
 
-## AdamParams
-
-Optimizer configuration.
-
+### AdamParams
 ```python
-from tinker.types import AdamParams
+from tinker import AdamParams
 
 adam = AdamParams(
     learning_rate=2e-4,
-    beta1=0.9,
-    beta2=0.999,
-    eps=1e-8,
-    weight_decay=0.0,
-    grad_clip_norm=1.0,
+    beta1=0.9,             # Gradient moving average
+    beta2=0.95,            # Gradient squared moving average
+    eps=1e-12,             # Numerical stability
+    weight_decay=0.0,      # Decoupled weight decay
+    grad_clip_norm=1.0,    # Global gradient norm clipping (0.0 = disabled)
 )
 ```
 
-## Helper functions (use these instead of manual construction)
+### LoraConfig
+```python
+from tinker import LoraConfig
+
+config = LoraConfig(
+    rank=32,               # LoRA rank
+    seed=None,             # Initialization seed
+    train_mlp=True,        # Train MLP layers
+    train_attn=True,       # Train attention layers
+    train_unembed=True,    # Train unembedding layer
+)
+```
+
+## Response types
 
-The cookbook provides helpers that handle the boilerplate:
+### ForwardBackwardOutput
+Returned by `forward_backward()` and `forward()`:
+```python
+result = tc.forward_backward(data=batch, loss_fn="cross_entropy")
+result.metrics              # dict[str, float] — training metrics (includes loss)
+result.loss_fn_outputs      # list[LossFnOutput] — per-sample outputs
+result.loss_fn_output_type  # str — loss output class name
+```
 
+### SampleResponse / SampledSequence
+Returned by `sample()`:
 ```python
-# SL: conversation → datum (full pipeline)
-from tinker_cookbook.supervised.data import conversation_to_datum
-datum = conversation_to_datum(messages, renderer, max_length, train_on_what)
+response = sc.sample(prompt=mi, num_samples=4, sampling_params=params)
+response.sequences                # list[SampledSequence]
+response.prompt_logprobs          # Optional[list[Optional[float]]] — per-prompt-token logprobs
+response.topk_prompt_logprobs     # Optional[list[Optional[list[tuple[int, float]]]]] — top-K
+
+for seq in response.sequences:
+    seq.tokens       # list[int] — generated token IDs
+    seq.logprobs     # Optional[list[float]] — per-token logprobs
+    seq.stop_reason  # StopReason: "length" | "stop"
+```
 
-# SL: model_input + weights → datum
-from tinker_cookbook.supervised.common import datum_from_model_input_weights
-datum = datum_from_model_input_weights(model_input, weights, max_length)
+### Other response types
+- `OptimStepResponse` — confirms parameter update
+- `SaveWeightsResponse` — `path: str` (tinker:// path to saved weights)
+- `LoadWeightsResponse` — confirms loaded weights
+- `GetInfoResponse` — `model_data: ModelData` (model_name, lora_rank, tokenizer_id)
+- `GetServerCapabilitiesResponse` — `supported_models: list[SupportedModel]`
+- `WeightsInfoResponse` — `base_model`, `lora_rank`, `is_lora`, `train_mlp`, `train_attn`, `train_unembed`
 
-# Renderer: messages → (model_input, weights)
-model_input, weights = renderer.build_supervised_example(messages)
+## Checkpoint and run types
+
+```python
+from tinker import TrainingRun, Checkpoint, CheckpointType, ParsedCheckpointTinkerPath
+
+# TrainingRun — metadata about a training run
+run.training_run_id    # str
+run.base_model         # str
+run.is_lora            # bool
+run.lora_rank          # Optional[int]
+run.last_checkpoint    # Optional[Checkpoint]
+run.user_metadata      # Optional[dict[str, str]]
+
+# Checkpoint — metadata about a saved checkpoint
+ckpt.checkpoint_id     # str
+ckpt.checkpoint_type   # CheckpointType: "training" | "sampler"
+ckpt.tinker_path       # str (tinker:// path)
+ckpt.size_bytes        # Optional[int]
+ckpt.public            # bool
+ckpt.expires_at        # Optional[datetime]
+
+# Parse a tinker:// path
+parsed = ParsedCheckpointTinkerPath.from_tinker_path("tinker://run-id/weights/ckpt-id")
+parsed.training_run_id  # str
+parsed.checkpoint_type  # CheckpointType
+parsed.checkpoint_id    # str
 ```
 
-See `tinker_cookbook/supervised/data.py` and `tinker_cookbook/supervised/common.py` for implementations.
+## Error types
+
+All exceptions inherit from `tinker.TinkerError`:
+- **`APIError`** → **`APIStatusError`**: `BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ConflictError` (409), `UnprocessableEntityError` (422), `RateLimitError` (429), `InternalServerError` (500+)
+- **`APIConnectionError`**, **`APITimeoutError`**, **`APIResponseValidationError`**
+- **`RequestFailedError`** — async request failure with error category
+
+## Cookbook helper functions
+
+Use these instead of manual Datum construction:
+- `tinker_cookbook.supervised.data.conversation_to_datum(messages, renderer, max_length, train_on_what)` — full SL pipeline
+- `tinker_cookbook.supervised.common.datum_from_model_input_weights(model_input, weights, max_length)` — from ModelInput + weights
+- `renderer.build_supervised_example(messages)` — returns `(ModelInput, weights)`
 
 ## Common pitfalls
-- Use helper functions (`conversation_to_datum`, `datum_from_model_input_weights`) instead of manual dict construction
+- Use helper functions instead of manual dict construction for Datum
 - `TensorData` wraps arrays — don't pass raw numpy/torch directly to `loss_fn_inputs`
 - `ModelInput.from_ints()` expects a flat list of integers, not nested lists
-- Call `datum.convert_tensors()` if you used torch.Tensor or numpy arrays directly in `loss_fn_inputs`
+- `ModelInput.length` is a property, not a method
+- Handle `tinker.RateLimitError` in production code with exponential backoff
PATCH

echo "Gold patch applied."
