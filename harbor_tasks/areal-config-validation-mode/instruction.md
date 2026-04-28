# areal-config-validation-mode

## Problem

The `WandBConfig` and `SwanlabConfig` dataclasses in `areal/api/cli_args.py` accept invalid mode values without any validation. Users can pass arbitrary strings like "invalid" or "test" to the `mode` field, and the configuration will be created silently without raising an error. This defers errors to later when the tracking libraries actually try to use these invalid modes, making debugging harder.

For example:
- `WandBConfig(mode="cloud")` should fail ("cloud" is a SwanLab mode, not WandB)
- `SwanlabConfig(mode="online")` should fail ("online" is a WandB mode, not SwanLab)
- Neither currently raises an error at initialization time.

## Expected Behavior

Both dataclasses should validate the `mode` field and raise a `ValueError` with a descriptive message if an invalid mode is provided:

**WandBConfig valid modes:** `online`, `offline`, `disabled`, `shared`
**SwanlabConfig valid modes:** `cloud`, `local`, `disabled`, `offline`

The error message should clearly indicate:
1. What field is invalid (e.g., "Invalid wandb mode" vs "Invalid swanlab mode")
2. What invalid value was provided
3. What the valid options are

## Files to Look At

- `areal/api/cli_args.py` — Contains the `WandBConfig` and `SwanlabConfig` dataclasses. You will need to find where these classes are defined and add appropriate validation.

## Notes

- The classes use `@dataclass` decorator
- The `mode` field may need its type hint updated to match the validation behavior

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
