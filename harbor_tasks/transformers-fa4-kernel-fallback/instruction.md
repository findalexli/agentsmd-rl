# Flash Attention 4 Kernel Fallback Not Working

## Bug Report

When a user requests `attn_implementation="flash_attention_4"` but does not have the native `flash_attn` package installed, the library should automatically fall back to a community kernel implementation via the `kernels` library, just as it does for Flash Attention 2 and 3. Currently, this fallback mechanism does not work for Flash Attention 4.

## Expected Behavior

The library uses the `FLASH_ATTENTION_COMPATIBILITY_MATRIX` to track supported Flash Attention versions, which includes versions 2, 3, and 4. When a native Flash Attention implementation is not available, the library should look up the corresponding community kernel package in `FLASH_ATTN_KERNEL_FALLBACK` and use that instead.

The existing fallback entries follow this naming convention:
- `"flash_attention_2"` maps to `"kernels-community/flash-attn2"`
- `"flash_attention_3"` maps to `"kernels-community/vllm-flash-attn3"`

When `flash_attention_4` is requested but not natively available, the library should similarly fall back to a `kernels-community/` package with an appropriate flash/attention-related name, following the same pattern as FA2 and FA3.

## Files to Investigate

- `src/transformers/modeling_utils.py` — contains the `_check_and_adjust_attn_implementation` method that iterates over `FLASH_ATTENTION_COMPATIBILITY_MATRIX.keys()` to handle kernel fallbacks
- `src/transformers/modeling_flash_attention_utils.py` — contains the `FLASH_ATTN_KERNEL_FALLBACK` dictionary that maps Flash Attention implementation names to their kernel community package names

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
