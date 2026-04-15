# Fix torch.Stream context manager reentrance

## Bug Description

The `torch.Stream` context manager in `torch/csrc/Stream.cpp` does not support nested or reentrant usage. When the same stream is used as a context manager multiple times (either nested with itself or interleaved with other streams), the `__enter__` method fails because it stores context (the previous stream and device) in a single `self->context` dict that gets overwritten on each `__enter__` call.

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

The `__enter__` method contains a `TORCH_CHECK` assertion with the message containing `"Stream's context should not be initialized."` that prevents reentrant use entirely.

Additionally, the destructor (`THPStream_dealloc`) does not clear `self->context`, causing a potential memory leak.

## Required Behavior

### 1. Remove the reentrance-blocking assertion

Remove the `TORCH_CHECK` assertion in `THPStream_enter` that contains `"context should not be initialized"`. Only `TORCH_INTERNAL_ASSERT` for stack invariants (e.g., asserting stack size > 0 in exit) is acceptable.

### 2. Use a stack-based context

Replace the single-dict context (where `self->context` was assigned via `dict.release()`) with a Python list that acts as a stack. Initialize `self->context` lazily as an empty list using `PyList_New(0)` on first `__enter__`.

### 3. `__enter__` pushes current state

`THPStream_enter` must:

- **No-op fast path**: Before switching streams, fetch the current stream via `getCurrentStream` and compare its id with `self->stream_id`. If the stream is already current, push `Py_None` onto the context stack as a sentinel and return early (increment refcount on self and return) — do **not** call `setCurrentStream` in this case.
- **Save and switch**: When the stream is not already current:
  - Read the current stream via `getCurrentStream` **before** calling `setCurrentStream` (to capture the previous state before it's overwritten)
  - Save the previous stream and device index into a dict with the keys `"_ctx_stream"` and `"_ctx_device_index"`
  - Append this dict to the context stack
  - Then call `setCurrentStream` to activate the new stream

### 4. `__exit__` pops and restores

`THPStream_exit` must:

- Read the top entry from the stack
- Pop only that single entry (do not unconditionally wipe the entire stack with `Py_CLEAR(self->context)` — unconditional clearing is only acceptable inside a conditional that checks if the stack is now empty)
- If the popped entry is `Py_None` (the no-op sentinel), do nothing and return
- Otherwise, extract the saved stream and device index from the dict using the keys `"_ctx_stream"` and `"_ctx_device_index"`, and call `setCurrentStream` to restore the previous stream

### 5. Destructor clears context

`THPStream_dealloc` must clear `self->context` (e.g., with `Py_CLEAR`) to prevent memory leaks. Follow the standard CPython deallocation ordering: call `PyObject_ClearWeakRefs` **before** clearing `self->context`, and end with `tp_free`.

### 6. Preserved patterns

- Keep `HANDLE_TH_ERRORS` / `END_HANDLE_TH_ERRORS` macros in both enter and exit functions
- Keep proper Python header includes (e.g., `structmember.h`)

## Files to Modify

- `torch/csrc/Stream.cpp`
