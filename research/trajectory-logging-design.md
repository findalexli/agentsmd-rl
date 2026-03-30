# Trajectory Logging Design: ATIF Format for Harbor RL Training

## 1. ATIF Trajectory Schema (v1.6)

The Agent Trajectory Interchange Format (ATIF) is defined by Pydantic models in
`harbor/src/harbor/models/trajectories/`. A `trajectory.json` file has this shape:

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
        {
          "tool_call_id": "string",
          "function_name": "string",
          "arguments": {}
        }
      ],
      "observation": {
        "results": [
          {
            "source_call_id": "string | null",
            "content": "string | [ContentPart] | null",
            "subagent_trajectory_ref": null
          }
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

**Validation constraints:**
- `step_id` values must be sequential starting at 1.
- Fields `model_name`, `reasoning_effort`, `reasoning_content`, `tool_calls`, `metrics`
  are only allowed when `source == "agent"`.
- `observation.results[].source_call_id` must reference a `tool_call_id` from the same step.
- `schema_version` must be one of the defined literals (use `"ATIF-v1.6"`).

## 2. Tinker-cookbook Internal Data Model

### Key types during rollout

| Tinker type | Location | Content |
|---|---|---|
| `Message` (TypedDict) | `renderers/base.py:584` | `{role, content, tool_calls?, tool_call_id?, name?}` |
| `ToolCall` (Pydantic) | `renderers/base.py:51` | `ToolCall(function=FunctionBody(name, arguments), id)` |
| `Transition` | `rl/types.py:71` | `{ob: ModelInput, ac: TokensWithLogprobs, reward, episode_done, metrics, logs}` |
| `Trajectory` | `rl/types.py:172` | `{transitions: [Transition], final_ob: ModelInput}` |
| `TrajectoryGroup` | `rl/types.py:306` | `{trajectories_G, final_rewards_G, metrics_G}` |
| `AgentToolMessageEnv` | `tool_use/agent_tool_message_env.py:29` | Holds `history: list[Message]` - **the full conversation** |
| `HarborEnvGroupBuilder` | `recipes/harbor_rl/harbor_env.py:83` | Holds `task: HarborTask` with task metadata |

### Data available at each level

**Inside `AgentToolMessageEnv.step()`** (turn-level):
- `self.history` -- full `list[Message]` so far, including the new assistant message, tool results
- Each `Message` has `role`, `content`, and optionally `tool_calls` (parsed ToolCall objects)
- `logs` dict with keys like `assistant_content`, `tool_call_0`, `tool_result_0`

**Inside `Transition`** (after env.step returns):
- `ob: ModelInput` -- tokenized observation (prompt tokens as ints, but no decoded text)
- `ac: TokensWithLogprobs` -- action tokens + per-token logprobs + stop_reason
- `reward`, `metrics`, `logs` (the logs contain decoded text snippets)

**Inside `TrajectoryGroup`** (after group rollout completes):
- List of `Trajectory` objects, each with its transitions
- Final rewards and group metrics
- The `EnvGroupBuilder` that created it (has `task: HarborTask`)

### The critical gap

The token-level `Trajectory` object does NOT retain the message-level `history`.
The `AgentToolMessageEnv` holds `history: list[Message]` during rollout,
but that object is discarded after the episode ends. The `Transition.logs` dict
contains text snippets but not structured tool calls.

**To get the full conversation, we must capture it from the MessageEnv before cleanup.**

## 3. Conversion: Tinker Messages -> ATIF Steps

### Mapping table

| Tinker Message field | ATIF Step field | Notes |
|---|---|---|
| `role == "system"` | `source: "system"` | First message typically |
| `role == "user"` | `source: "user"` | Task instruction, tool results |
| `role == "assistant"` | `source: "agent"` | Model's response |
| `role == "tool"` | (merged into previous agent step's `observation`) | Tool execution results |
| `message["content"]` | `step.message` | String content |
| `message["tool_calls"]` | `step.tool_calls` | Convert ToolCall format |
| `ToolCall.function.name` | `tool_calls[].function_name` | Direct mapping |
| `ToolCall.function.arguments` | `tool_calls[].arguments` | Parse JSON string to dict |
| `ToolCall.id` | `tool_calls[].tool_call_id` | Direct mapping |
| `TokensWithLogprobs.tokens` | `metrics.completion_token_ids` | Token IDs |
| `TokensWithLogprobs.logprobs` | `metrics.logprobs` | Per-token logprobs |

### Conversion algorithm

```
For each tinker Message in history:
  If role == "system":
    -> ATIF Step(source="system", message=content)

  If role == "user" AND no preceding assistant step needs tool results:
    -> ATIF Step(source="user", message=content)

  If role == "assistant":
    -> ATIF Step(source="agent", message=content, tool_calls=..., metrics=...)
    Collect following role=="tool" messages into observation.results[]

  If role == "tool":
    -> Append to previous agent step's observation.results[]
    Set source_call_id = message["tool_call_id"]
    Set content = message["content"]
```

The key subtlety: ATIF bundles tool results as `observation` on the **same step** as the
agent's tool calls. Tinker's `history` has them as separate `Message` objects with `role="tool"`.

## 4. Hook Points in the Training Loop

### Option A: MessageEnv-level hook (recommended)

**Where:** Subclass `AgentToolMessageEnv` or wrap `HarborEnvGroupBuilder`

The cleanest approach is to capture `self.history` inside the MessageEnv when the episode
ends (when `step()` returns `episode_done=True`). At that point the full structured
conversation is available.

```python
class TrajectoryCapturingMessageEnv(AgentToolMessageEnv):
    """Wraps AgentToolMessageEnv to capture the message history for ATIF export."""

    captured_history: list[Message] | None = None

    async def step(self, message: Message) -> MessageStepResult:
        result = await super().step(message)
        if result.episode_done:
            self.captured_history = list(self.history)
        return result
```

Then, in `HarborEnvGroupBuilder.make_envs()`, wrap each env so the message env is
accessible. After `do_group_rollout` returns, extract histories from the envs before cleanup.

### Option B: Post-rollout hook in the training loop

**Where:** `do_sync_training()` at line ~1752, right after `results_P` is collected and
before `_maybe_export_rollout_summary_jsonl`.

At this point we have `env_group_builders_P` (with task metadata) and
`trajectory_groups_P` (with transitions). If we've captured histories via Option A,
we can access them through the builder/env references.

### Option C: Parallel to `_maybe_export_rollout_summary_jsonl`

The existing `_maybe_export_rollout_summary_jsonl` call is the natural sibling location.
We add `_maybe_export_atif_trajectories` right next to it, using the same data.

### Recommended approach: Combine A + C

1. Subclass the message env to capture histories.
2. Store captured histories on the `HarborEnvGroupBuilder` (alongside `_sandboxes`).
3. After rollout, before cleanup, extract and convert to ATIF.
4. Write trajectory.json files alongside the existing rollout summary JSONL.

## 5. W&B Integration Options

### Current W&B support in tinker-cookbook

`ml_log.py` defines `WandbLogger` which wraps `wandb.init()` and `wandb.log()`.
It only logs scalar metrics via `wandb.log(metrics, step=step)`. The `MultiplexLogger`
fans out to JSON + console + W&B + Neptune + Trackio.

The training loop calls `ml_logger.log_metrics(metrics, step=i_batch)` at the end of
each iteration. There is no existing support for logging artifacts, HTML, or tables.

### Integration options

#### Option 1: W&B Artifacts (for batch trajectory storage)

```python
import wandb

artifact = wandb.Artifact(f"trajectories-iter-{i_batch}", type="trajectories")
artifact.add_dir(trajectory_output_dir)  # Add all trajectory.json files
wandb.log_artifact(artifact)
```

**Pros:** Versioned, downloadable, searchable in W&B UI.
**Cons:** Not inline-viewable; requires downloading to inspect.

#### Option 2: W&B HTML panels (for in-dashboard viewing)

```python
# Render trajectory as HTML (reuse Harbor viewer's rendering)
html_content = render_trajectory_html(trajectory)
wandb.log({"trajectory/task_name": wandb.Html(html_content)}, step=i_batch)
```

**Pros:** Viewable directly in W&B dashboard.
**Cons:** Need to build or extract the HTML renderer; HTML panels can be heavy.

#### Option 3: W&B Tables (for structured analysis)

```python
table = wandb.Table(columns=["task", "reward", "num_turns", "trajectory_json"])
for task_name, reward, traj_json in trajectories:
    table.add_data(task_name, reward, num_turns, json.dumps(traj_json))
wandb.log({"trajectories": table}, step=i_batch)
```

**Pros:** Filterable, sortable in W&B; can do reward-vs-length scatter plots.
**Cons:** Large JSON strings in table cells; no rich rendering.

#### Option 4: Combined approach (recommended)

- **Every iteration:** Log a W&B Table with summary columns (task, reward, num_turns,
  has_tool_calls, total_tokens) for quick analysis.
- **Every N iterations or on eval:** Log the full trajectory.json files as a W&B Artifact
  for archival and Harbor viewer compatibility.
- **Optionally:** Log 1-2 representative trajectories as `wandb.Html` for at-a-glance
  inspection in the dashboard.

### Implementation sketch for WandbLogger extension

```python
class ATIFWandbLogger:
    """Extends WandbLogger with trajectory logging capabilities."""

    def log_trajectories(
        self,
        trajectories: list[dict],  # ATIF trajectory dicts
        task_names: list[str],
        rewards: list[float],
        step: int,
    ) -> None:
        # Summary table
        table = wandb.Table(
            columns=["task", "reward", "num_steps", "num_tool_calls"]
        )
        for traj, task, reward in zip(trajectories, task_names, rewards):
            steps = traj["steps"]
            n_tool_calls = sum(
                len(s.get("tool_calls", []) or [])
                for s in steps if s["source"] == "agent"
            )
            table.add_data(task, reward, len(steps), n_tool_calls)
        wandb.log({"train/trajectories": table}, step=step)

    def log_trajectory_artifact(
        self,
        output_dir: Path,
        step: int,
    ) -> None:
        artifact = wandb.Artifact(
            f"atif-trajectories-{step:06d}",
            type="atif-trajectories",
        )
        artifact.add_dir(str(output_dir))
        wandb.log_artifact(artifact)
```

## 6. Harbor Viewer Compatibility

### How `harbor view` works

`harbor view <folder>` starts a FastAPI server that:
1. Scans `<folder>/` for job directories containing trial directories.
2. Each trial has `agent/trajectory.json` (ATIF format) and `result.json`.
3. The `/api/jobs/{job}/trials/{trial}/trajectory` endpoint reads and returns the raw JSON.
4. The frontend renders the trajectory in a step-by-step viewer.

### Directory structure expected

```
<folder>/
  <job-name>/
    config.json         # JobConfig
    result.json         # JobResult (aggregate stats)
    <trial-name>/
      result.json       # TrialResult (per-trial)
      agent/
        trajectory.json # ATIF format -- THIS IS WHAT WE PRODUCE
      verifier/
        reward.txt
        test-stdout.txt
        test-stderr.txt
```

### Making our output compatible

For our RL training trajectories to work with `harbor view`, we need to:

1. **Write trajectory.json** in ATIF v1.6 format (validated via Harbor's Pydantic models).
2. **Organize files** in the expected hierarchy. We can write them under
   `{log_path}/harbor_view/{job-name}/{trial-name}/agent/trajectory.json`.
3. **Write stub result.json** files so the scanner discovers them.

Alternatively, for simpler integration, we can write standalone trajectory.json files
and load them programmatically without the full job/trial hierarchy.

## 7. Implementation Plan

### Phase 1: Core converter module

**File:** `agentsmd_rl/atif_converter.py`

- Function `messages_to_atif_steps(history: list[Message]) -> list[Step]`
  - Walks the Message list, groups tool results with their agent step
  - Assigns sequential step_ids
  - Converts ToolCall format (tinker -> ATIF)
- Function `build_atif_trajectory(session_id, agent_name, model_name, steps, ...) -> dict`
  - Constructs the full ATIF dict, validated via Harbor's Pydantic models
- Function `inject_token_metrics(steps, transitions: list[Transition]) -> None`
  - Enriches agent steps with completion_token_ids, logprobs from Transition.ac
- Unit tests with example message sequences

### Phase 2: Message history capture

**File:** `agentsmd_rl/capturing_env.py`

- `CapturingAgentToolMessageEnv(AgentToolMessageEnv)` -- captures `self.history` on done
- `CapturingHarborEnvGroupBuilder(HarborEnvGroupBuilder)` -- wraps make_envs to use
  the capturing env, stores histories after rollout
- Expose `get_captured_histories() -> list[list[Message]]` for each env in the group

### Phase 3: Training loop integration

**File:** `agentsmd_rl/trajectory_logger.py`

- `ATIFTrajectoryLogger` class:
  - `log_iteration(i_batch, env_builders, trajectory_groups, output_dir)` -- called
    after each iteration, parallel to `_maybe_export_rollout_summary_jsonl`
  - Converts each trajectory to ATIF, writes to `{iter_dir}/atif/`
  - Optionally writes harbor-view-compatible directory structure
- Hook into training via a wrapper around the harbor_rl recipe's `cli_main`,
  or by monkey-patching `_maybe_export_rollout_summary_jsonl` to also call our logger

### Phase 4: W&B integration

**File:** `agentsmd_rl/wandb_trajectory.py`

- `WandbTrajectoryLogger`:
  - Wraps wandb table + artifact logging
  - Called from `ATIFTrajectoryLogger.log_iteration` when wandb is active
- Extend `ml_log.setup_logging` or add our logger to the MultiplexLogger

### Phase 5: Harbor viewer bridge

- Script or config to symlink/copy the ATIF output into harbor-view-compatible layout
- Or: minimal `result.json` stubs so `harbor view` can discover our trajectories

### Files to create in agentsmd_rl/

```
agentsmd_rl/
  atif_converter.py        # Phase 1: Message -> ATIF conversion
  capturing_env.py         # Phase 2: MessageEnv wrapper for history capture
  trajectory_logger.py     # Phase 3: Training loop integration
  wandb_trajectory.py      # Phase 4: W&B table/artifact logging
  harbor_view_export.py    # Phase 5: Export to harbor view layout
```

### Files to modify

- None in tinker-cookbook (we wrap/extend, not modify upstream)
- `agentsmd_rl/__init__.py` -- register exports
- Training launch script (the entrypoint that calls `cli_main`) -- inject our loggers

### Estimated complexity

| Phase | Effort | Dependencies |
|---|---|---|
| Phase 1 (converter) | ~200 LOC | harbor models (import or redefine) |
| Phase 2 (capture) | ~100 LOC | tinker-cookbook env classes |
| Phase 3 (logger) | ~150 LOC | Phase 1 + 2 |
| Phase 4 (wandb) | ~100 LOC | wandb SDK |
| Phase 5 (viewer) | ~80 LOC | Phase 3 |

Total: ~630 LOC of production code + tests.

### Key risk: Message history access

The main challenge is that `AgentToolMessageEnv.history` is internal to the env object,
which is created inside `make_envs()` and not directly accessible after rollout. The
capturing env subclass (Phase 2) solves this by storing histories on the builder before
cleanup destroys the sandboxes.

If subclassing proves awkward (e.g., pickling issues with process-pool executors), a
fallback is to reconstruct messages from `Transition.logs` (which contain
`assistant_content`, `tool_call_*`, `tool_result_*` keys). This is lossy but workable
for display purposes.
