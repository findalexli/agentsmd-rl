# Fix CPU-Only Import Failure in Memory Cache System

## Problem

On machines without CUDA installed, importing certain modules in the SGLang memory cache system fails with an `ImportError: libcuda.so.1: cannot open shared object file`.

## Symptoms

- Attempting to import the memory cache modules on CPU-only machines produces an error loading the CUDA library
- The error propagates through the import chain when the modules are accessed
- Two pure-Python hash utility functions are needed by multiple components but are currently inaccessible on systems without CUDA

## Requirements

After the fix, the following must hold:

1. **Functions must be accessible without CUDA dependencies:**
   - `get_hash_str(tokens, prior_hash=None)` - returns SHA256 hex string of token IDs
   - `hash_str_to_int64(hash_str)` - returns signed int64 from first 16 hex characters of hash

2. **Correct behavior for `get_hash_str`:**
   - Must compute SHA256 of little-endian 32-bit token values
   - Must handle token lists (e.g., `[1, 2, 3]`)
   - Must handle bigram tuples for EAGLE mode (e.g., `[(1, 2), (3, 4]`)
   - When `prior_hash` is provided, must incorporate it by hashing the prior hash bytes followed by the new tokens

3. **Correct behavior for `hash_str_to_int64`:**
   - Must take a hex string and return a signed int64
   - Must interpret the first 16 hex characters as a uint64 value
   - Must convert values >= 2^63 to negative numbers by subtracting 2^64

4. **Import sites must use the following exact import string:**
   - `from sglang.srt.mem_cache.utils import get_hash_str`
   - `from sglang.srt.mem_cache.utils import hash_str_to_int64`
   - The file `radix_cache.py` must import both functions using this pattern
   - The file `cache_controller.py` must import `get_hash_str` using this pattern

5. **Cleanup requirements:**
   - The hash functions must no longer be defined in `hicache_storage.py`
   - No function definitions named `get_hash_str` or `hash_str_to_int64` should remain in that file

6. **Code quality:**
   - All modified files must have valid Python syntax
   - Functions must have non-trivial implementations (not `pass` or `...` stubs)
   - Code must pass ruff checks for F401 (unused imports) and F821 (undefined names)
   - Code must be formatted with black and isort
