# Missing encoder_only attribute causes run failure

## Problem

The `launch_server_process()` function in `slime/backends/sglang_utils/sglang_engine.py` directly accesses `server_args.encoder_only` without checking whether the attribute exists. When `worker_type` is `"regular"`, the `ServerArgs` object does not have the `encoder_only` attribute, causing an `AttributeError` crash:

```
File "slime/backends/sglang_utils/sglang_engine.py", line 54, in launch_server_process
    if server_args.encoder_only:
AttributeError: 'ServerArgs' object has no attribute 'encoder_only'
```

The `encoder_only` attribute is only present on `ServerArgs` when certain worker types or configurations are used. The code needs to handle the case where it is absent.

## Expected Behavior

The function should safely check whether `server_args` has the `encoder_only` attribute before accessing it. When the attribute is missing, the function should fall through to the default (non-encoder-only) import path.

## File to Modify

- `slime/backends/sglang_utils/sglang_engine.py` -- the `launch_server_process()` function
