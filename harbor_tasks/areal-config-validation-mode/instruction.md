# areal-config-validation-mode

## Problem

The `WandBConfig` and `SwanlabConfig` dataclasses in `areal/api/cli_args.py` accept invalid mode values without any validation. Users can pass arbitrary strings like "invalid" or "test" to the `mode` field, and the configuration will be created silently without raising an error. This defers errors to later when the tracking libraries actually try to use these invalid modes, making debugging harder.

For example:
- `WandBConfig(mode="cloud")` should fail ("cloud" is a SwanLab mode, not WandB)
- `SwanlabConfig(mode="online")` should fail ("online" is a WandB mode, not SwanLab)
- Neither currently raises an error at initialization time.

## Expected Behavior

Both dataclasses should validate the `mode` field in their `__post_init__` method and raise a `ValueError` with a descriptive message if an invalid mode is provided:

**WandBConfig valid modes:** `online`, `offline`, `disabled`, `shared`
**SwanlabConfig valid modes:** `cloud`, `local`, `disabled`, `offline`

The error message should clearly indicate:
1. What field is invalid (wandb mode vs swanlab mode)
2. What invalid value was provided
3. What the valid options are

## Files to Look At

- `areal/api/cli_args.py` — Contains the `WandBConfig` and `SwanlabConfig` dataclasses (around lines 1968-2015). Look for where these classes are defined and where validation should be added.

## Notes

- The classes use `@dataclass` decorator
- `SwanlabConfig` already has a `__post_init__` method that handles `api_key` initialization — you'll need to add validation there
- `WandBConfig` does not currently have a `__post_init__` method — you'll need to add one
- The `mode` field type hint was `str | None` in SwanlabConfig but should be just `str` after the fix (matching the validation behavior)
