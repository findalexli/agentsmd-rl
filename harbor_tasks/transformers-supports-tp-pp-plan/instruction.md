# Fix: supports_tp_plan and supports_pp_plan always return True

## Problem

The `supports_tp_plan` and `supports_pp_plan` properties on `PreTrainedModel` always return `True`, even for models that do not have tensor parallelism or pipeline parallelism plans. This breaks any logic that conditionally enables TP/PP based on model support.

## Root Cause

In `src/transformers/modeling_utils.py`:

- In configs, `base_model_tp_plan` and `base_model_pp_plan` default to `None`.
- In models, `_tp_plan` and `_pp_plan` class variables appear to default to `None`, but `post_init` always sets them to empty dicts `{}`.
- The `supports_tp_plan` and `supports_pp_plan` properties check `is not None`, which is always `True` for an empty dict.

So the checks `self._tp_plan is not None` and `self._pp_plan is not None` always pass because `post_init` converts `None` to `{}`.

Additionally:
- The `pp_plan` setter lacks input validation (unlike `tp_plan`'s setter).
- The `_pp_plan` type hint incorrectly uses a `PipelineParallel` Enum type that does not match actual usage (it should be `dict[str, tuple[str, str]]`).
- The `supports_pp_plan` property does not check `config.base_model_pp_plan`.

## Expected Fix

- Change `is not None` checks to truthiness checks (empty dict is falsy).
- Add input validation to the `pp_plan` setter.
- Fix the `_pp_plan` type hint.
- Add config check to `supports_pp_plan`.
- Remove the unused `PipelineParallel` Enum.

## Files to Investigate

- `src/transformers/modeling_utils.py` -- `supports_tp_plan`, `supports_pp_plan`, `pp_plan` setter, `_pp_plan` type hint
