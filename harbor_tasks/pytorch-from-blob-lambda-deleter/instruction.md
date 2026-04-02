# Bug: `torch::stable::from_blob` cannot accept capturing lambdas as deleters

## Context

The stable ABI layer in PyTorch (`torch/csrc/stable/`) provides a C-compatible interface for creating tensors from external memory blobs via `torch_from_blob`. This function accepts an optional deleter callback that gets invoked when the tensor's storage is deallocated.

## Problem

The current `torch_from_blob` function in `torch/csrc/stable/c/shim.h` accepts the deleter as a plain C function pointer: `void (*deleter)(void*)`. The corresponding C++ wrapper in `torch/csrc/stable/ops.h` passes this directly.

This design means that **capturing lambdas cannot be used as deleters**. In C++, a capturing lambda is not convertible to a plain function pointer because it carries state. This is a significant limitation for users of the stable ABI who need to associate cleanup state with their tensor memory (e.g., tracking allocation counts, releasing resources from custom allocators, etc.).

## Files involved

- `torch/csrc/stable/c/shim.h` — C ABI declaration of `torch_from_blob`
- `torch/csrc/stable/ops.h` — C++ header-only wrapper `torch::stable::from_blob` (the overload that takes a deleter)
- `torch/csrc/shim_common.cpp` — Implementation of `torch_from_blob`

## Expected behavior

`torch::stable::from_blob` should accept both plain function pointers and capturing lambdas as the deleter argument. The C ABI boundary needs to be bridged in a way that allows stateful callables to be passed through.

## Scope

The fix should be limited to the three files listed above. The non-deleter overload of `from_blob` should remain unchanged. The solution must be backwards-compatible with existing callers that pass plain function pointers.
