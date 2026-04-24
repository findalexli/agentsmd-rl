# Fix: Legacy RoPE parameters ignored when passed as kwargs

## Symptom

When a `PreTrainedConfig` subclass receives `rope_scaling` and `rope_theta` as constructor arguments (e.g., when loading a config JSON saved from an older model), those parameters are silently ignored unless the config class explicitly defines `rope_parameters` as a class attribute. This causes:

- Configurations that rely on legacy-format RoPE keys to fail validation after config tightening
- RoPE parameters set as arbitrary attributes instead of being normalized into the `rope_parameters` dict

## Expected Behavior

1. **Conversion**: When a config is constructed with `rope_scaling` and `rope_theta` in kwargs, these should be converted to the `rope_parameters` dict format. The legacy `rope_scaling` value uses the format `{"type": <scaling_type>, "factor": <factor>}`. After conversion, the resulting `rope_parameters` dict must contain the original keys from `rope_scaling` — in particular, `config.rope_parameters.get("rope_theta")` must equal the `rope_theta` kwarg value, and `config.rope_parameters.get("factor")` must equal the `"factor"` value from the `rope_scaling` dict. This must work regardless of whether the config class defines `rope_parameters` as a class attribute.

2. **Warning**: A warning should be logged (at WARNING level) via the module-level logger in `transformers.configuration_utils` when legacy RoPE kwargs are used on a config that doesn't define `rope_parameters`. The warning message should reference `rope_scaling` or `rope_parameters`.

3. **Backward compatibility**: Configs that already define `rope_parameters` as a class attribute must continue to work unchanged.

4. **Non-stub requirement**: The fix must not be a minimal stub. The code implementing the fix must contain substantive logic — at least 5 non-trivial statements, where "non-trivial" means the statement is not a `pass` statement and is not a bare expression statement (such as a standalone docstring).

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
