# Bug: `torch::stable::from_blob` cannot accept capturing lambdas as deleters

## Context

The stable ABI layer in PyTorch provides a C-compatible interface for creating tensors from external memory blobs via `torch_from_blob`. This function accepts an optional deleter callback that gets invoked when the tensor's storage is deallocated.

## Problem

Currently, `torch_from_blob` accepts the deleter as a plain C function pointer: `void (*deleter)(void*)`. The corresponding C++ wrapper passes this directly as a `DeleterFnPtr`.

This means that **capturing lambdas cannot be used as deleters**. In C++, a capturing lambda is not convertible to a plain function pointer because it carries state. This is a significant limitation for users of the stable ABI who need to associate cleanup state with their tensor memory (e.g., tracking allocation counts, releasing resources from custom allocators, etc.).

## Requirements

The fix must satisfy the following specifications:

### C ABI: two-argument deleter with context pointer

The C-level `torch_from_blob` declaration must change its deleter parameter from a single-argument function pointer to a two-argument callback that receives both the data pointer and a caller-supplied context pointer. The new parameter pair should be:

- `void (*deleter_callback)(void* data, void* ctx)` — the deleter function
- `void* deleter_ctx` — opaque context pointer forwarded to the callback

### C++ wrapper: template with SFINAE

The C++ `from_blob` overload that accepts a deleter must be converted to a template that accepts any callable type `F`. The template must use `std::is_invocable_v<F, void*>` for SFINAE to constrain the callable type, ensuring only types invocable with a `void*` argument are accepted.

### Implementation: wrapping lambda that forwards context

The implementation of `torch_from_blob` must bridge between the two-argument C-style callback and the single-argument deleter expected by the underlying `at::for_blob()` API. This must be done via a wrapping lambda that captures both the callback and context, specifically: `[deleter_callback, deleter_ctx](void* ...)` which calls `deleter_callback(data, deleter_ctx)`.

### Backward compatibility

- Existing callers that pass plain function pointers must continue to work.
- The existing no-deleter overload of `from_blob` must remain unchanged.
- A nullptr guard for the deleter callback must be preserved.