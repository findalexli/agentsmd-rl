# Bug: `torch::stable::from_blob` cannot accept capturing lambdas as deleters

## Context

The stable ABI layer in PyTorch (`torch/csrc/stable/`) provides a C-compatible interface for creating tensors from external memory blobs via `torch_from_blob`. This function accepts an optional deleter callback that gets invoked when the tensor's storage is deallocated.

## Problem

The current `torch_from_blob` function in `torch/csrc/stable/c/shim.h` accepts the deleter as a plain C function pointer: `void (*deleter)(void*)`. The corresponding C++ wrapper in `torch/csrc/stable/ops.h` passes this directly as a `DeleterFnPtr`.

This design means that **capturing lambdas cannot be used as deleters**. In C++, a capturing lambda is not convertible to a plain function pointer because it carries state. This is a significant limitation for users of the stable ABI who need to associate cleanup state with their tensor memory (e.g., tracking allocation counts, releasing resources from custom allocators, etc.).

## Files involved

- `torch/csrc/stable/c/shim.h` — C ABI declaration of `torch_from_blob`
- `torch/csrc/stable/ops.h` — C++ header-only wrapper `torch::stable::from_blob` (the overload that takes a deleter)
- `torch/csrc/shim_common.cpp` — Implementation of `torch_from_blob`

## Expected behavior

The `from_blob` function family must support stateful deleters (capturing lambdas) alongside plain function pointers. This requires coordinated changes across all three files:

### C ABI declaration (`shim.h`)

The `torch_from_blob` declaration must change from a single-argument deleter `void (*deleter)(void*)` to a two-argument callback `void (*deleter)(void* data, void* ctx)` plus an additional `void*` context parameter. This allows passing both a cleanup function and an associated state pointer through the C ABI boundary.

### C++ wrapper (`ops.h`)

The deleter-accepting overload of `from_blob` must become a function template that accepts any callable type `F`, constrained via SFINAE using `std::is_invocable_v<F, void*>`. This replaces the hardcoded `DeleterFnPtr` parameter type so that capturing lambdas and other stateful callables are accepted.

The template implementation must handle two cases at the C ABI boundary:
- When `F` is convertible to `DeleterFnPtr`: pass the function pointer through as the context, with a trampoline callback that casts it back and invokes it.
- When `F` is not convertible (e.g., a capturing lambda): heap-allocate the callable, pass it as the context pointer, and have the callback invoke and delete it.

The existing no-deleter overload of `from_blob` must remain unchanged and continue using `aoti_torch_create_tensor_from_blob`.

### Implementation (`shim_common.cpp`)

The `torch_from_blob` implementation must accept the two-arg deleter callback and context pointer with parameters named `deleter_callback` (the two-arg function pointer) and `deleter_ctx` (the `void*` context). When `deleter_callback` is not null, the implementation must create a wrapping lambda that captures both `deleter_callback` and `deleter_ctx`, takes a single `void*` data argument, and forwards the call as `deleter_callback(data, deleter_ctx)`. This wrapping lambda bridges the two-arg C callback back to the single-arg callable expected by `at::for_blob().deleter()`.

The existing nullptr guard for the deleter callback must be preserved for backward compatibility.

## Scope

The fix should be limited to the three files listed above. The solution must be backwards-compatible with existing callers that pass plain function pointers.
