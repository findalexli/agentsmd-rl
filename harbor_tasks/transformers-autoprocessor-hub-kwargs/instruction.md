# Fix: AutoProcessor.from_pretrained silently dropping hub kwargs

## Problem

`AutoProcessor.from_pretrained` silently drops hub kwargs like `force_download`, `cache_dir`, `token`, `revision`, etc. This means users cannot control caching, authentication, or versioning when loading processors through the auto class.

## Root Cause

In `src/transformers/models/auto/processing_auto.py`, the `from_pretrained` method filters kwargs for `cached_file` using `inspect.signature(cached_file).parameters`. However, `cached_file` is defined as:

```python
def cached_file(path_or_repo_id, filename, **kwargs):
```

Since it uses `**kwargs`, `inspect.signature` only sees three parameter names: `path_or_repo_id`, `filename`, and `kwargs`. Hub parameters like `force_download`, `cache_dir`, `token`, `revision`, etc. are never matched by the filter and get silently dropped before reaching the `cached_file` calls.

## Expected Fix

Replace the `inspect.signature` filtering with an explicit tuple of the hub parameter names that `cached_file` actually accepts. This is consistent with how other auto classes like `AutoTokenizer` handle the same situation -- they pass hub kwargs explicitly by name. Also remove the now-unused `import inspect`.

## Files to Investigate

- `src/transformers/models/auto/processing_auto.py` -- the `from_pretrained` class method
