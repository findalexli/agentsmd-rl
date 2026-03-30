# Fix: rope_theta validation fails when stored inside rope_parameters dict

## Problem

Some models (e.g., GLM-4.6V) store `rope_theta` inside a `rope_parameters` dictionary in the HuggingFace config rather than as a top-level config attribute. The validation code in `slime/backends/megatron_utils/arguments.py` compares against `config.rope_theta`, which returns a stale class default (10000) instead of the actual value (e.g., 500000 from `rope_parameters`).

This causes validation failures when launching training with the correct `--rotary-base 500000` because the validation sees the wrong value.

## Root Cause

The `hf_validate_args` function in `arguments.py` includes `("rope_theta", "rotary_base", equal)` in the validation loop, which directly accesses `hf_config.rope_theta`. When the model stores `rope_theta` inside `rope_parameters` dict, the direct attribute access returns the class default instead of the actual configured value.

## Expected Behavior

Before the validation loop, check if `rope_parameters` dict exists and contains `rope_theta`. If so, use that value. Otherwise fall back to `hf_config.rope_theta`. Remove `rope_theta` from the generic validation loop and validate it separately with the resolved value.

## File to Modify

- `slime/backends/megatron_utils/arguments.py` -- the `hf_validate_args` function
