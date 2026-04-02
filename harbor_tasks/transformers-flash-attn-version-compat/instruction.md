# Backward-Compatibility Break: Missing Flash Attention Version Helper

## Bug Report

After a recent refactor of the flash attention utilities in `src/transformers/utils/import_utils.py`, a previously exported convenience function for checking whether flash attention version 2.10+ is installed was removed. This function was part of the public API surface exported from `src/transformers/utils/__init__.py`.

Downstream code and third-party libraries that import this helper from `transformers.utils` now get an `ImportError` at import time, breaking backward compatibility.

## Relevant Files

- `src/transformers/utils/import_utils.py` — where flash attention version-check utilities are defined (see the `is_flash_attn_greater_or_equal` function around line 961)
- `src/transformers/utils/__init__.py` — the public re-export surface for utils

## Expected Behavior

The removed helper should be restored so that existing imports continue to work, but it should also guide users toward the newer, more general version-checking API with an appropriate deprecation warning.

## Reproduction

```python
from transformers.utils import is_flash_attn_greater_or_equal_2_10
# ImportError: cannot import name 'is_flash_attn_greater_or_equal_2_10' from 'transformers.utils'
```
