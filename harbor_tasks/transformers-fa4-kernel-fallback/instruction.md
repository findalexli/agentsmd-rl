# Flash Attention 4 Kernel Fallback Not Working

## Bug Report

When a user requests `attn_implementation="flash_attention_4"` but does not have the native `flash_attn` package installed, the library is supposed to fall back to a community kernel implementation via the `kernels` library. This fallback mechanism works correctly for Flash Attention 2 and 3, but Flash Attention 4 is explicitly skipped in the fallback loop.

There are two issues:

1. In `src/transformers/modeling_utils.py`, the method `_check_and_adjust_attn_implementation` iterates over all known Flash Attention versions to check if a kernel fallback is needed. However, version 4 is explicitly skipped with a `continue` statement, preventing the fallback logic from ever activating for FA4.

2. In `src/transformers/modeling_flash_attention_utils.py`, the `FLASH_ATTN_KERNEL_FALLBACK` dictionary maps Flash Attention implementation names to their kernel community package names. The entry for `"flash_attention_4"` is missing, so even if the skip were removed, the fallback lookup would fail with a `KeyError`.

## Relevant Files

- `src/transformers/modeling_utils.py` — see the `_check_and_adjust_attn_implementation` classmethod, specifically the loop over `FLASH_ATTENTION_COMPATIBILITY_MATRIX.keys()` (around line 1817)
- `src/transformers/modeling_flash_attention_utils.py` — see the `FLASH_ATTN_KERNEL_FALLBACK` dictionary (around line 62)

## Expected Behavior

When `flash_attention_4` is requested but not natively available, the library should automatically fall back to the corresponding community kernel package, just as it does for FA2 and FA3.
