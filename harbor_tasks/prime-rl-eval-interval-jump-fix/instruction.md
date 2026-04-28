# Fix skipped eval intervals when `ckpt_step` jumps over interval boundaries

## Background

`prime-rl` is an async-RL training library. The orchestrator (`src/prime_rl/orchestrator/orchestrator.py`) periodically pauses to run online evaluations (evals) on the current model checkpoint. Eval cadence is controlled by `config.eval.interval` — for example, `interval=25` means "run evals at checkpoint steps 0, 25, 50, 75, …" (the step-0 case being optional, gated by `eval_base_model`).

When `strict_async_level=False`, the inference and training loops advance asynchronously. As a result, the value of `ckpt_step` (driven by `update_policy()` in the scheduler, which sets it to `max(async_away, latest_ckpt_step)`) is **not guaranteed to land on every integer in sequence**. From one orchestrator iteration to the next, `ckpt_step` can jump over interval-aligned values — e.g. it can advance from `24` straight to `26`, skipping `25`.

## Symptom

Today the orchestrator decides whether to run an eval using a **strict modulo equality** check:

```python
if (
    config.eval
    and ckpt_step % config.eval.interval == 0
    and ckpt_step > last_eval_step
    and ((ckpt_step == 0 and config.eval.eval_base_model) or ckpt_step > 0)
):
    ...
```

Because of the `% interval == 0` clause, an iteration that observes `ckpt_step=26` with `interval=25` will not fire an eval at all — even though the run *passed through* the interval boundary at 25 since the previous iteration. The eval for that interval is silently and permanently dropped.

This was observed on a real training run: with `interval=25`, the step-25 eval never ran because `ckpt_step` jumped 24 → 26 between two orchestrator iterations.

## Required behavior

Add a helper named **`compute_eval_ckpt_step`** to `src/prime_rl/orchestrator/eval_utils.py` and update the orchestrator's eval-trigger block to use it.

### Signature

```python
def compute_eval_ckpt_step(
    ckpt_step: int,
    prev_ckpt_step: int,
    last_eval_step: int,
    interval: int,
    eval_base_model: bool = True,
) -> int | None:
    ...
```

### Contract

The function decides which interval-aligned step (if any) the current orchestrator iteration should run an eval *for*, given that `ckpt_step` may have jumped from `prev_ckpt_step` over one or more interval boundaries since the previous iteration. It must:

1. **Return `None` if `ckpt_step <= prev_ckpt_step`.** No forward progress, no eval.
2. **Compute the highest interval-aligned step in the half-open range `(prev_ckpt_step, ckpt_step]`.** Concretely, that is `(ckpt_step // interval) * interval`, but only if it is strictly greater than `prev_ckpt_step`.
3. **Return that interval step** when it is strictly greater than `last_eval_step` (so the same interval is never eval'd twice).
4. **Special-case interval step `0`** (the base-model eval): only return `0` when `ckpt_step == 0` *and* `eval_base_model` is true. Otherwise return `None` for the zero case.
5. Otherwise return `None`.

### Worked examples

| `ckpt_step` | `prev_ckpt_step` | `last_eval_step` | `interval` | `eval_base_model` | result |
|---|---|---|---|---|---|
| 25 | 24 | 0  | 25 | (default) | `25` (exact hit) |
| 26 | 24 | 0  | 25 | (default) | `25` (jumped over boundary — the bug) |
| 23 | 22 | 0  | 25 | (default) | `None` (no boundary crossed) |
| 0  | -1 | -1 | 25 | `True`    | `0`  (base-model eval enabled) |
| 0  | -1 | -1 | 25 | `False`   | `None` (base-model eval disabled) |
| 25 | 24 | 25 | 25 | (default) | `None` (already eval'd at 25) |
| 25 | 25 | 0  | 25 | (default) | `None` (no progress) |
| 76 | 24 | 0  | 25 | (default) | `75` (multiple boundaries crossed — return the highest) |
| 51 | 48 | 25 | 25 | (default) | `50` |

End-to-end: simulating `ckpt_step` trajectory `[0, 0, 3, 5, 10, 15, 20, 24, 26, 30, 35, 40, 48, 51, 60, 70, 74, 76]` with `interval=25` (starting `prev_ckpt_step=-1`, `last_eval_step=-1`, `eval_base_model=True`) must fire evals at exactly `[0, 25, 50, 75]` — never twice for the same interval, never skipping one.

### Wiring in the orchestrator

The orchestrator's per-iteration eval-trigger block in `src/prime_rl/orchestrator/orchestrator.py` currently inlines the broken modulo check. Replace it with a call to `compute_eval_ckpt_step`, threading whatever additional state (such as the previous iteration's `ckpt_step`) the new logic needs. The orchestrator file must remain syntactically valid Python.

## Code Style Requirements

This repo's `AGENTS.md` lays down two rules you must follow:

- **Avoid `try`/`except`** unless it is genuinely necessary (fault-tolerance / retries). For this task, no exception handling is needed — write straight-line code.
- **Do not add unnecessary comments.** No `# previously this did X` or change-narration. Keep targeted comments only where they explain non-obvious intent.

Tests in this repo are **plain pytest functions with fixtures, never class-based**.

The repo's CI enforces **ruff** linting (version 0.13.0, configured in `pyproject.toml`). Any file you modify must pass `ruff check --config=pyproject.toml` without errors.

## Files to modify

- `src/prime_rl/orchestrator/eval_utils.py` — add the new function.
- `src/prime_rl/orchestrator/orchestrator.py` — import and use it in the eval-trigger block; track `prev_ckpt_step`.
