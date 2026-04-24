# Missing backward-compatibility alias for `check_model_inputs`

## Bug

The function `check_model_inputs` in `src/transformers/utils/generic.py` was recently renamed to `merge_with_config_defaults`. However, no backward-compatibility alias was added for the old name. Downstream libraries (e.g., vllm) that import `check_model_inputs` from `transformers.utils.generic` now get an `ImportError`.

## Expected behavior

Importing `check_model_inputs` from `transformers.utils.generic` should still work. It should emit a deprecation warning indicating that `check_model_inputs` is deprecated in favor of `merge_with_config_defaults`, and then delegate to the new function.

## Steps to reproduce

```python
from transformers.utils.generic import check_model_inputs
# ImportError: cannot import name 'check_model_inputs' from 'transformers.utils.generic'
```

## Relevant files

- `src/transformers/utils/generic.py` — contains `merge_with_config_defaults` (the renamed function, around line 863)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
