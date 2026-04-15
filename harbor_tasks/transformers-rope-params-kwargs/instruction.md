# Fix: Legacy RoPE parameters ignored when passed as kwargs to configs without rope_parameters attribute

## Symptom

When a `PreTrainedConfig` subclass receives `rope_scaling` and `rope_theta` as constructor arguments (e.g., when loading a config JSON saved from an older model), those parameters are silently ignored unless the config class explicitly defines `rope_parameters` as a class attribute. This causes:

- Configurations that rely on legacy-format RoPE keys to fail validation after config tightening
- RoPE parameters set as arbitrary attributes instead of being normalized into the `rope_parameters` dict

## Expected Behavior

1. **Conversion**: When a config is constructed with `rope_scaling` and `rope_theta` in kwargs, these should be converted to the `rope_parameters` dict format (with `rope_theta` as a key inside `rope_parameters`), regardless of whether the class defines `rope_parameters` as an attribute.

2. **Warning**: A warning should be emitted so users are notified their config uses the legacy RoPE format. The warning message should reference `rope_scaling` or `rope_parameters`.

3. **Backward compatibility**: Configs that already define `rope_parameters` as a class attribute must continue to work unchanged.

4. **Non-stub requirement**: The `__post_init__` method must contain at least 5 non-trivial statements (not counting `pass` or docstring-only expressions).