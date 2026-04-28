# Improve Archon pipeline parallelism memory handling

You are working in the `AReaL` repository (a distributed RL training
framework whose Archon engine is the experimental pipeline-parallel
training backend). The repo is checked out at the working directory.
Read `AGENTS.md`, `CLAUDE.md`, and any rules under `.claude/rules/`
before changing code; the repo enforces strict conventions.

The Archon engine's pipeline-parallel (PP) path has three memory and
ergonomics gaps that this task asks you to close. Each is observable
from outside the engine, even on CPU.

## 1. Add an `is_moe_model_config` utility

`areal/experimental/models/archon/utils.py` exposes helpers that look at
a HuggingFace `PretrainedConfig`-like object (anything with attributes
such as `num_experts` / `num_local_experts`). It is missing a
public utility that answers a simple yes/no question: *does this config
describe a Mixture-of-Experts (MoE) model?*

Add a function with the signature

```python
def is_moe_model_config(model_config: object) -> bool: ...
```

with the following contract:

- Looks for `num_experts` first; if absent (or `None`), falls back to
  `num_local_experts`.
- Returns `True` only when an expert-count attribute exists *and* its
  value is greater than 1 (i.e. an actual MoE with multiple experts).
- Returns `False` for dense models, missing attributes, `None`, or a
  degenerate value of 1.
- Has a docstring.

Export the new symbol via the module's `__all__`.

## 2. Free per-microbatch logits during PP training

When `ForwardBackwardRunner._run_train` in
`areal/experimental/engine/archon_runner.py` calls
`schedule.step(...)` (PyTorch's pipeline scheduler), the last stage
appends every microbatch's output (logits) to its
`output_stage.output_chunks` list. Because training only cares about
the loss (computed *inside* the loss-fn passed to the schedule), those
logits are dead weight: they pile up in memory until `step()` returns,
adding `N * sizeof(logits)` bytes of peak memory for `N` microbatches.

Fix this without touching PyTorch's internals: introduce a small
list-like shim whose `.append(...)` is a no-op, swap it onto
`output_stage.output_chunks` for the duration of the train step, then
restore a regular empty `list` afterwards so subsequent `eval()`
invocations on the same stage can still collect outputs normally.

Constraints:

- The shim must be a subclass of `list` (PyTorch's pipelining code
  treats `output_chunks` as a list — `isinstance(x, list)` checks and
  `clear()`/iteration must keep working).
- Only `append` is overridden; everything else inherits from `list`.
- When the runner is on a non-last stage (`self.has_last_stage` is
  `False`), do not touch `output_chunks` at all.
- After `schedule.step` returns, restore `output_stage.output_chunks`
  to a fresh empty `list` so a later `_run_eval` call on the same
  stage can append outputs and read them.

Also: `_run_eval` currently returns processed outputs without freeing
`output_stage.output_chunks`, so subsequent calls keep accumulating
across iterations. Clear the list after reading from it.

## 3. Make the FSDP "reshard after forward" policy configurable

`ArchonEngineConfig` in `areal/api/cli_args.py` currently hard-codes
`reshard_after_forward_policy="default"` at every FSDP call site. This
removes a knob that matters in PP+FSDP setups: with PP enabled, FSDP
otherwise keeps parameters unsharded after forward, which trades
memory for fewer all-gathers; users may want to override that.

Add a new field on `ArchonEngineConfig`:

- Name: `reshard_after_forward_policy`
- Type: `str`
- Default: `"default"`
- Allowed values: exactly `"default"`, `"always"`, `"never"` — nothing
  else.
- Includes a `help` string in its dataclass metadata describing the
  three modes, and a `choices` list with the three allowed values.
- Field is added with a default so existing configs keep working
  (backward-compat rule from `.claude/rules/api-config.md`).

In `__post_init__`, validate the value: if it is not one of the three
allowed strings, raise `ValueError`. The exception message **must**
include both the field name `reshard_after_forward_policy` and all
three valid choices `default`, `always`, `never`, so a misconfiguring
user immediately sees what is allowed.

Wire the new field through both Archon FSDP call sites (the regular
`_apply_parallelism` and the PP-specific `_apply_pipeline_parallelism`
paths) so the previously hard-coded `"default"` argument now reads
from `self.config.archon.reshard_after_forward_policy`.

## 4. While you're in the engine: tighten two related details

These are small but observable changes already implied by the work above.

- `ArchonEngine.initialize` already disables `torch.compile` for
  zero-bubble PP schedules. It should *also* disable
  `torch._functorch.config.donated_buffer` — but **only for MoE
  models** (use the new utility from §1). Dense models do not need
  this. Use `self.logger` (which uses `areal.utils.logging` per the
  project's logging rule) to log the change at `INFO`.
- `_prepare_mb_list` in `archon_engine.py` validates that
  `n_seqs >= pp_size`. With virtual stages this is too loose: it
  should require `n_seqs >= num_total_stages` where
  `num_total_stages = pp_size * stages_per_rank` (and
  `stages_per_rank = len(self.pp_stages)`). Update the check, the
  `min_n_mbs` value, and the error message accordingly.

## Code Style Requirements

The repo enforces strict style and tests will run the project's own
linters on your changed files:

- **`ruff` 0.14.9** — both `ruff check` and `ruff format --check` must
  pass on every file you modify. Configuration lives in the repo's
  `pyproject.toml` (`[tool.ruff]`).
- **No wildcard imports** (`from x import *`) — see `AGENTS.md`.
- **Logging** uses `areal.utils.logging.getLogger("PascalCaseName")`,
  not `print` or stdlib `logging.getLogger(__name__)` — see
  `.claude/rules/code-style.md`.
- **Config dataclasses** follow `.claude/rules/api-config.md`:
  validation in `__post_init__` raising `ValueError`, fields exposed
  to the CLI carry a clear `help` in metadata, new fields ship with a
  default for backward compatibility.

## What "done" looks like

The behaviors above are what the test suite checks. As a sanity guide:

- A standalone import of
  `areal/experimental/models/archon/utils.py` exposes
  `is_moe_model_config` and it returns the documented truth values for
  configs with various `num_experts` / `num_local_experts`.
- The `_NullOutputChunks` class is defined as a top-level class in
  `archon_runner.py` (so an AST/import inspection can find it by
  name), subclasses `list`, and its `append` discards the argument.
- `ArchonEngineConfig()` constructs cleanly; the new field's default
  is the literal string `"default"`; passing
  `reshard_after_forward_policy="invalid"` raises `ValueError` with a
  message containing `reshard_after_forward_policy`, `default`,
  `always`, `never`.
- `ruff check` and `ruff format --check` pass on the four
  PR-modified Python files.
