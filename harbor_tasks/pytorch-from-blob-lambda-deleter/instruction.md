# Bug: `torch::stable::from_blob` cannot accept capturing lambdas as deleters

## Context

The stable ABI layer in PyTorch provides a C-compatible interface for creating tensors from external memory blobs via `torch_from_blob` (declared in `torch/csrc/stable/c/shim.h`, implemented in `torch/csrc/shim_common.cpp`). This function accepts an optional deleter callback invoked when the tensor's storage is deallocated. The C++ `from_blob` overload that accepts a deleter is in `torch/csrc/stable/ops.h`.

Currently the deleter is passed as a plain C function pointer: `void (*deleter)(void*)`. A capturing lambda cannot be used as a deleter because it is not convertible to a plain function pointer.

## Problem

Calling `torch_from_blob` with a capturing lambda fails to compile, because:
1. A capturing lambda is not a plain function pointer — it carries captured state
2. The current C ABI only accepts a single-argument function pointer `void (*)(void*)`
3. There is no way to pass an additional context argument to associate state with the callback

This limits users of the stable ABI who need to release custom allocation resources or track cleanup state.

## Requirements

### Two-argument C ABI

The `torch_from_blob` declaration in `shim.h` must accept a two-argument callback that receives both the data pointer and a caller-supplied context pointer. This allows callers to pass arbitrary state through the context argument.

### C++ wrapper for capturing lambdas

The `from_blob` overload in `ops.h` that accepts a deleter must be able to accept callable types beyond plain function pointers — specifically, it must work with capturing lambdas. The implementation should not assume the deleter is `DeleterFnPtr`.

### Context forwarding

The implementation in `shim_common.cpp` must pass the context argument through to the callback when the tensor's storage is deallocated.

### Backward compatibility

- Existing callers passing plain function pointers must continue to work without modification
- The no-deleter overload of `from_blob` must remain unchanged
- A nullptr guard for the deleter callback must be preserved