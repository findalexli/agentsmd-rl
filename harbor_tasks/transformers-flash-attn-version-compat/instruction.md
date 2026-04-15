# Backward-Compatibility Break: Missing Flash Attention Version Helper

## Bug Report

After a recent refactor of the flash attention utilities, a previously exported convenience function `is_flash_attn_greater_or_equal_2_10` was removed from the public API surface of the `transformers` library.

The "2_10" suffix in the function name refers to **semantic version 2.1.0** (since 2.1.0 equals 2.10 in semver).

Downstream code and third-party libraries that import this helper from `transformers.utils` now get an `ImportError` at import time, breaking backward compatibility.

## Expected Behavior

The removed helper should be restored so that existing imports continue to work. It must satisfy all of the following:

1. **Importability**: `is_flash_attn_greater_or_equal_2_10` must be importable directly from `transformers.utils` and be callable.

2. **Version-checking semantics**: When called with no arguments, the function must return a `bool` indicating whether the installed `flash_attn` package version is >= 2.1.0:
   - `True` for versions >= 2.1.0 (e.g., 2.1.0, 2.5.0, 2.11.0)
   - `False` for versions < 2.1.0 (e.g., 1.9.5, 2.0.0, 2.0.9)
   - `False` when `flash_attn` is not installed at all

3. **Deprecation warning**: When called, the function must emit either a `FutureWarning` or `DeprecationWarning`. The warning message must contain at least one of the following keywords: "deprecat" (matching "deprecate"/"deprecated"/"deprecation"), "removed", or "use " — guiding users toward the newer, more general version-checking API.

4. **No regressions**: Existing utility functions (e.g., `is_torch_available`, `is_flash_attn_2_available`) and the more general `is_flash_attn_greater_or_equal` must remain importable and functional. All existing repository consistency checks must continue to pass.

## Reproduction

```python
from transformers.utils import is_flash_attn_greater_or_equal_2_10
# ImportError: cannot import name 'is_flash_attn_greater_or_equal_2_10' from 'transformers.utils'
```
