# Trajectory Logging Design: ATIF Format for Harbor RL Training

## 1. ATIF Trajectory Schema (v1.6)

Defined by Pydantic models in `harbor/src/harbor/models/trajectories/`. A `trajectory.json` shape:

```json
{
  "schema_version": "ATIF-v1.6",
  "session_id": "string (UUID-style unique ID for the run)",
  "agent": {
    "name": "string",
    "version": "string",
    "model_name": "string | null",
    "tool_definitions": [{"name": "...", "description": "...", "parameters": {...}}],
    "extra": {}
  },
  "steps": [
    {
      "step_id": 1,
      "timestamp": "ISO 8601 | null",
      "source": "system | user | agent",
      "model_name": "string | null  (agent-only)",
      "reasoning_effort": "string | float | null  (agent-only)",
      "message": "string | [ContentPart]",
      "reasoning_content": "string | null  (agent-only)",
      "tool_calls": [
        {"tool_call_id": "string", "function_name": "string", "arguments": {}}
      ],
      "observation": {
        "results": [
          {"source_call_id": "string | null", "content": "string | [ContentPart] | null", "subagent_trajectory_ref": null}
        ]
      },
      "metrics": {
        "prompt_tokens": "int | null",
        "completion_tokens": "int | null",
        "cached_tokens": "int | null",
        "cost_usd": "float | null",
        "prompt_token_ids": "[int] | null",
        "completion_token_ids": "[int] | null",
        "logprobs": "[float] | null",
        "extra": {}
      },
      "is_copied_context": "bool | null",
      "extra": {}
    }
  ],
  "notes": "string | null",
  "final_metrics": {
    "total_prompt_tokens": "int | null",
    "total_completion_tokens": "int | null",
    "total_cached_tokens": "int | null",
    "total_cost_usd": "float | null",
    "total_steps": "int | null",
    "extra": {}
  },
  "continued_trajectory_ref": "string | null",
  "extra": {}
}
```

**Constraints**: `step_id` sequential from 1; `model_name`, `reasoning_effort`, `reasoning_content`, `tool_calls`, `metrics` only when `source == "agent"`; `observation.results[].source_call_id` must reference a `tool_call_id` from the same step; `schema_version` must be `"ATIF-v1.6"`.

## 2. Tinker-cookbook Internal Data Model

### Key types during rollout

| Tinker type | Location | Content |
|---|---|---|
| `Message` (TypedDict) | `renderers/base.py:584` | `{role, content, tool_calls?, tool_call_id?, name?}` |
| `ToolCall` (Pydantic) | `renderers/base.py:51` | `ToolCall(function=FunctionBody(name, arguments), id)` |
| `Transition` | `rl/types.py:71` | `{ob: ModelInput, ac: TokensWithLogprobs, reward, episode_done, metrics, logs}` |
| `Trajectory` | `rl/types.py:172` | `{transitions: [Transition], final_ob: ModelInput}` |
| `TrajectoryGroup` | `rl/types.py:306` | `{trajectories_G, final_rewards_G, metrics_G}` |
| `AgentToolMessageEnv` | `tool_use/agent_tool_message_env.py:29` | Holds `history: list[Message]` — **the full conversation** |
| `HarborEnvGroupBuilder` | `recipes/harbor_rl/harbor_env.py:83` | Holds `task: HarborTask` |

### Data available at each level

| Level | What's there |
|---|---|
| `AgentToolMessageEnv.step()` (turn) | `self.history`: full `list[Message]` so far, including new assistant message and tool results. Each `Message` has `role`, `content`, optionally parsed `tool_calls`. Plus a `logs` dict (`assistant_content`, `tool_call_0`, `tool_result_0`). |
| `Transition` (post step) | `ob: ModelInput` (tokenized prompt, no decoded text); `ac: TokensWithLogprobs` (action tokens + per-token logprobs + stop_reason); `reward`, `metrics`, `logs` (text snippets). |
| `TrajectoryGroup` (post group) | List of `Trajectory`, each with transitions; final rewards and group metrics; the `EnvGroupBuilder` (has `task: HarborTask`). |

### The critical gap

The token-level `Trajectory` does NOT retain the message-level `history`. `AgentToolMessageEnv` holds it during rollout but discards after the episode. `Transition.logs` has text snippets, not structured tool calls. **We must capture from the MessageEnv before cleanup.**

## 3. Conversion: Tinker Messages → ATIF Steps

### Mapping table

| Tinker | ATIF | Notes |
|---|---|---|
| `role == "system"` | `source: "system"` | First message typically |
| `role == "user"` | `source: "user"` | Task instruction, tool results |
| `role == "assistant"` | `source: "agent"` | Model response |
| `role == "tool"` | merged into previous agent step's `observation` | Tool result |
| `message["content"]` | `step.message` | String content |
| `message["tool_calls"]` | `step.tool_calls` | Convert format |
| `ToolCall.function.name` | `tool_calls[].function_name` | Direct |
| `ToolCall.function.arguments` | `tool_calls[].arguments` | Parse JSON string → dict |
| `ToolCall.id` | `tool_calls[].tool_call_id` | Direct |
| `TokensWithLogprobs.tokens` | `metrics.completion_token_ids` | Token IDs |
| `TokensWithLogprobs.logprobs` | `metrics.logprobs` | Per-token logprobs |

### Conversion algorithm

```
For each tinker Message in history:
  If role == "system":  -> ATIF Step(source="system", message=content)
  If role == "user" AND no preceding assistant step needs tool results:
                        -> ATIF Step(source="user", message=content)
  If role == "assistant":
                        -> ATIF Step(source="agent", message=content, tool_calls=..., metrics=...)
                           Collect following role=="tool" messages into observation.results[]
  If role == "tool":    -> Append to previous agent step's observation.results[]
                           source_call_id = message["tool_call_id"]
                           content = message["content"]
```

Subtlety: ATIF bundles tool results as `observation` on the **same step** as the agent's tool calls. Tinker's `history` has them as separate `Message` objects with `role="tool"`.

## 4. Hook Points in the Training Loop

### Option A — MessageEnv-level hook (recommended)

Subclass `AgentToolMessageEnv` or wrap `HarborEnvGroupBuilder`. Capture `self.history` when `step()` returns `episode_done=True` — at that point the full structured conversation is available.

```python
class TrajectoryCapturingMessageEnv(AgentToolMessageEnv):
    captured_history: list[Message] | None = None

    async def step(self, message: Message) -> MessageStepResult:
        result = await super().step(message)
        if result.episode_done:
            self.captured_history = list(self.history)
        return result
```

In `HarborEnvGroupBuilder.make_envs()`, wrap each env so the message env is accessible. After `do_group_rollout` returns, extract histories before cleanup.

### Other options (rejected)

| Option | Where | Why rejected |
|---|---|---|
| B: Post-rollout in training loop | `do_sync_training()` ~1752, after `results_P` | Requires history already captured (Option A) — not standalone |
| C: Sibling to `_maybe_export_rollout_summary_jsonl` | Same call site | Good colocation but still needs Option A for data |

### Recommended: A + C combined

1. Subclass message env to capture histories.
2. Store on `HarborEnvGroupBuilder` (alongside `_sandboxes`).
3. After rollout, before cleanup, extract and convert to ATIF.
4. Write `trajectory.json` files alongside the existing rollout summary JSONL.

## 5. W&B Integration Options

`ml_log.py` defines `WandbLogger` (wraps `wandb.init()` / `wandb.log()`), scalar metrics only. `MultiplexLogger` fans out to JSON + console + W&B + Neptune + Trackio. Training loop calls `ml_logger.log_metrics(metrics, step=i_batch)` per iteration. No existing artifact / HTML / table support.

| Option | Mechanism | Pros | Cons |
|---|---|---|---|
| 1 — Artifacts | `wandb.Artifact("trajectories-iter-{i}", type="trajectories"); add_dir; log_artifact` | Versioned, downloadable, searchable | Not inline-viewable |
| 2 — HTML panels | `wandb.log({"trajectory/task": wandb.Html(html)}, step=i)` | Inline in dashboard | Need renderer; HTML panels heavy |
| 3 — Tables | `wandb.Table(columns=[...])` per task | Filterable, sortable, scatter plots | Large JSON in cells, no rich rendering |
| **4 — Combined (recommended)** | Per-iter table (summary) + every-N-iter Artifact (full JSON) + 1-2 HTML samples | All three benefits | More plumbing |

### Implementation sketch

```python
class ATIFWandbLogger:
    def log_trajectories(self, trajectories, task_names, rewards, step):
        table = wandb.Table(columns=["task", "reward", "num_steps", "num_tool_calls"])
        for traj, task, reward in zip(trajectories, task_names, rewards):
            steps = traj["steps"]
            n_tool_calls = sum(len(s.get("tool_calls", []) or [])
                               for s in steps if s["source"] == "agent")
            table.add_data(task, reward, len(steps), n_tool_calls)
        wandb.log({"train/trajectories": table}, step=step)

    def log_trajectory_artifact(self, output_dir, step):
        artifact = wandb.Artifact(f"atif-trajectories-{step:06d}", type="atif-trajectories")
        artifact.add_dir(str(output_dir))
        wandb.log_artifact(artifact)
```

## 6. Harbor Viewer Compatibility

`harbor view <folder>` starts a FastAPI server that scans `<folder>/` for job dirs containing trial dirs (each with `agent/trajectory.json` + `result.json`). The `/api/jobs/{job}/trials/{trial}/trajectory` endpoint returns raw JSON; the frontend renders step-by-step.

Expected layout:

```
<folder>/
  <job-name>/
    config.json         # JobConfig
    result.json         # JobResult (aggregate stats)
    <trial-name>/
      result.json       # TrialResult (per-trial)
      agent/
        trajectory.json # ATIF -- THIS IS WHAT WE PRODUCE
      verifier/
        reward.txt
        test-stdout.txt
        test-stderr.txt
```

To be compatible:

1. Write `trajectory.json` in ATIF v1.6 (validated via Harbor's Pydantic models).
2. Use the hierarchy: `{log_path}/harbor_view/{job-name}/{trial-name}/agent/trajectory.json`.
3. Stub `result.json` files so the scanner discovers them.

Alternative: standalone `trajectory.json` files loaded programmatically without the full hierarchy.

## 7. Implementation Plan

### Phases

| Phase | File | What |
|---|---|---|
| 1 — Converter | `agentsmd_rl/atif_converter.py` | `messages_to_atif_steps(history) → list[Step]`, `build_atif_trajectory(...) → dict`, `inject_token_metrics(steps, transitions)` enriching agent steps with `completion_token_ids`/`logprobs`. Unit tests with example sequences. |
| 2 — Capture | `agentsmd_rl/capturing_env.py` | `CapturingAgentToolMessageEnv` (captures `self.history` on done); `CapturingHarborEnvGroupBuilder` wrapping `make_envs`; `get_captured_histories()` per env. |
| 3 — Logger | `agentsmd_rl/trajectory_logger.py` | `ATIFTrajectoryLogger.log_iteration(...)` parallel to `_maybe_export_rollout_summary_jsonl`. Converts to ATIF, writes `{iter_dir}/atif/`. Hook via wrapper around harbor_rl `cli_main` or monkey-patch `_maybe_export_rollout_summary_jsonl`. |
| 4 — W&B | `agentsmd_rl/wandb_trajectory.py` | `WandbTrajectoryLogger` table + artifact, called from Phase 3 when wandb active. Extend `ml_log.setup_logging` or add to MultiplexLogger. |
| 5 — Viewer | `agentsmd_rl/harbor_view_export.py` | Symlink/copy ATIF output into harbor-view layout, or stub `result.json` files. |

### Files to modify

- None in tinker-cookbook (we wrap/extend, never modify upstream).
- `agentsmd_rl/__init__.py` — register exports.
- Training launch script (entrypoint calling `cli_main`) — inject loggers.

### Estimated complexity

| Phase | LOC | Dependencies |
|---|---:|---|
| 1 (converter) | ~200 | harbor models (import or redefine) |
| 2 (capture) | ~100 | tinker-cookbook env classes |
| 3 (logger) | ~150 | Phases 1+2 |
| 4 (wandb) | ~100 | wandb SDK |
| 5 (viewer) | ~80 | Phase 3 |

Total: ~630 LOC + tests.

### Key risk: Message history access

`AgentToolMessageEnv.history` is internal to an env created inside `make_envs()`, not directly accessible after rollout. The capturing subclass (Phase 2) solves this by storing histories on the builder before sandbox cleanup.

If subclassing proves awkward (pickling issues with process-pool executors), fallback: reconstruct from `Transition.logs` keys (`assistant_content`, `tool_call_*`, `tool_result_*`). Lossy, workable for display.
