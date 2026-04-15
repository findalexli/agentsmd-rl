# Fix: Parallel plan support checks always return True

## Problem

In the huggingface/transformers repository (commit `09fea1e6e970a1051b1141ce320a3d696b2c15ed`), the `PreTrainedModel` class has properties `supports_tp_plan` and `supports_pp_plan` that indicate whether a model supports tensor parallelism or pipeline parallelism. These properties always return `True`, even for models that have no parallelism plans configured.

Specific issues:

1. **Empty plans treated as supported**: `supports_tp_plan` and `supports_pp_plan` return `True` even when the plan variables are empty dictionaries `{}`. They should return `False` when no non-empty plan exists from any source (the model's own plan, its base model's plan, or its config's plan).

2. **Missing config check for PP**: `supports_pp_plan` does not check `config.base_model_pp_plan`, whereas `supports_tp_plan` correctly checks `config.base_model_tp_plan`. Models with PP plans defined only in their config are not detected as PP-capable.

3. **pp_plan setter lacks input validation**: The `pp_plan` setter accepts any value without raising an error. It should raise a `ValueError` for non-dict, non-None inputs (e.g. strings, integers, lists, booleans, tuples).

4. **pp_plan setter mishandles None**: When `None` is assigned via the `pp_plan` setter, it is stored as `None` instead of being converted to an empty dictionary `{}`.

5. **Unused PipelineParallel enum**: A `PipelineParallel` enum class exists in the module but is unused. The `_pp_plan` type hint on `PreTrainedModel` references this enum instead of using the correct type `dict[str, tuple[str, str]]`.

## Expected Behavior

- `supports_tp_plan` returns `False` when all of `_tp_plan`, `base_model._tp_plan`, and `config.base_model_tp_plan` are empty dicts or `None`. Returns `True` when any of them is a non-empty dict.
- `supports_pp_plan` returns `False` when all of `_pp_plan`, `base_model._pp_plan`, and `config.base_model_pp_plan` are empty dicts or `None`. Returns `True` when any of them is a non-empty dict.
- The `pp_plan` setter accepts dict values (storing them as-is), accepts `None` (converting to `{}`), and raises `ValueError` for any other input type.
- The `PipelineParallel` enum class is removed entirely, along with the `from enum import Enum` import if no longer needed.
- The `_pp_plan` type hint uses `dict[str, tuple[str, str]]` without `| None`.
- All changes must pass `ruff check` and `ruff format --check`.
