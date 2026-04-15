# AttributeError when accessing encoder_only attribute

## Problem

The `launch_server_process()` function in `slime/backends/sglang_utils/sglang_engine.py` directly accesses `server_args.encoder_only`. When `server_args` is constructed without an `encoder_only` attribute, this raises an `AttributeError`.

## Expected Behavior

When `encoder_only` is absent or falsy, the function should proceed with the default non-encoder-only import path and launch the server successfully without crashing.

## File to Modify

- `slime/backends/sglang_utils/sglang_engine.py` -- the `launch_server_process()` function