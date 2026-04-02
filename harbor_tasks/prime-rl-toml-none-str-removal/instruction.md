# TOML Config Serialization Writes Literal "None" Strings

## Problem

When the RL, SFT, and inference entrypoints write resolved configs to disk as TOML files, they use a custom helper function `none_to_none_str` (defined in `src/prime_rl/utils/config.py`) to handle Python `None` values. This function recursively walks the config dict and converts every `None` to the literal string `"None"` before passing it to `tomli_w.dump()`.

This approach is fragile:

- It pollutes TOML config files with fake `"None"` string values that are semantically meaningless in TOML
- It requires a matching deserializer (`_none_str_to_none`) on the read path to undo the conversion
- The recursive walk is unnecessary complexity when cleaner serialization options exist

## Affected Files

- `src/prime_rl/utils/config.py` -- defines the `none_to_none_str` and `_convert_none` helpers
- `src/prime_rl/entrypoints/rl.py` -- imports and uses `none_to_none_str` in `write_config` and `write_subconfigs`
- `src/prime_rl/entrypoints/sft.py` -- imports and uses `none_to_none_str` in `write_config`
- `src/prime_rl/entrypoints/inference.py` -- imports and uses `none_to_none_str` in `write_config`

## Expected Behavior

Config serialization should cleanly omit fields with `None` values rather than writing them as the string `"None"`. The custom helper functions should be removed in favor of Pydantic's built-in mechanism for excluding `None` values during serialization.
