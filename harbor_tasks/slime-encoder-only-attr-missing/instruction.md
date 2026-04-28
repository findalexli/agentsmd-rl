# AttributeError when accessing encoder_only attribute

## Problem

The `launch_server_process()` function in `slime/backends/sglang_utils/sglang_engine.py` directly accesses `server_args.encoder_only`. When a regular (non-encoder) worker type is used, the `ServerArgs` object is constructed without an `encoder_only` attribute, causing the following crash:

```
AttributeError: 'ServerArgs' object has no attribute 'encoder_only'
```

This crash occurs during engine initialization. The `SglangEngine` class calls `launch_server_process(ServerArgs(**server_args_dict))`, and the `server_args_dict` dictionary only contains an `encoder_only` key when the worker type is explicitly configured as an encoder. For regular worker types, the key is absent entirely, so `ServerArgs(**server_args_dict)` produces an object without the `encoder_only` attribute.

The bug was reported when running with a regular (non-encoder) worker configuration. Encoder-type workers are unaffected because `encoder_only` is present in their args dictionary.

## Expected Behavior

When `encoder_only` is absent or falsy, the function should proceed with the default non-encoder import path and launch the server successfully without crashing. When `encoder_only` is explicitly `True`, the encode-server import path should still be used (this is the existing correct behavior and must be preserved). The function must create a real multiprocessing process with a callable target in all cases.

## File to Modify

- `slime/backends/sglang_utils/sglang_engine.py` — the `launch_server_process()` function

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black` (Python formatter)
- `ruff` (Python linter)
- `isort` (import sorting, with `--profile=black`)