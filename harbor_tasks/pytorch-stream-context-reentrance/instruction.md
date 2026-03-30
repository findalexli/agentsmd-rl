# Fix torch.Stream context manager reentrance

## Bug Description

The `torch.Stream` context manager in `torch/csrc/Stream.cpp` does not support nested or reentrant usage. When the same stream is used as a context manager multiple times (either nested with itself or interleaved with other streams), the `__exit__` method fails because it stores context (the previous stream and device) in a single `self->context` dict that gets overwritten on each `__enter__` call.

This means the following valid patterns crash or produce incorrect behavior:

```python
import torch
s0 = torch.Stream()

# Reentrant: same stream used twice
with s0, s0:  # __enter__ on s0 overwrites context from first __enter__
    pass
# __exit__ tries to restore, but context was overwritten -- crash or wrong stream restored

# Nested: interleaved streams
s1 = torch.Stream()
with s0:
    with s1:
        with s0:  # crashes: s0.context already set, assertion fails
            pass
```

The `__enter__` method has an assertion `TORCH_CHECK(!(self->context), "Stream's context should not be initialized.")` that prevents reentrant use entirely. The context management needs to be changed from a single dict to a stack-based approach so that each `__enter__` pushes state and each `__exit__` pops it.

Additionally, the destructor (`THPStream_dealloc`) does not clear the context, causing a potential memory leak.

## Files to Modify

- `torch/csrc/Stream.cpp`
