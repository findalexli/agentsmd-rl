# TOML Config Serialization Writes Literal "None" Strings

## Problem

When the RL, SFT, and inference entrypoints write resolved configs to disk as TOML files, the output contains literal `"None"` string values wherever a config field has a Python `None` value. This makes the TOML files semantically incorrect (TOML has no null type, and the string `"None"` is not a valid TOML value) and requires a matching deserializer on the read path to undo the conversion.

## Expected Behavior

When writing a config with optional/nullable fields that are `None`, those fields should not appear in the TOML output at all, rather than being serialized as the string `"None"`.

## Affected Files

- `src/prime_rl/utils/config.py` -- helper functions used during TOML serialization
- `src/prime_rl/entrypoints/rl.py` -- RL trainer entrypoint (`write_config`, `write_subconfigs`)
- `src/prime_rl/entrypoints/sft.py` -- SFT entrypoint (`write_config`)
- `src/prime_rl/entrypoints/inference.py` -- inference entrypoint (`write_config`)

## Validation

After fixing, running the entrypoints to write config files should produce TOML output with no `"None"` string literals and no fields present for values that were `None` in the original config.
