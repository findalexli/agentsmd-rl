# Task: Add MSan Support for Fibers and Fix Dragonbox Struct Padding

## Problem

The ClickHouse codebase has issues with Memory Sanitizer (MSan) support for fiber context tracking. There are two related problems:

1. **Missing BOOST_USE_MSAN definition**: The boost fiber implementation has MSan annotations (`__msan_start_switch_fiber`/`__msan_finish_switch_fiber`) around every `swapcontext` call, but they were gated on `BOOST_USE_MSAN` which was never defined in the CMake configuration. Without these annotations, MSan loses track of shadow memory across fiber context switches, causing false positives.

2. **Struct padding shadow tracking**: MSan tracks shadow per-field in LLVM IR, not per-byte of the padded struct representation. When a struct with padding is returned by value, the padding bytes have no shadow entry and appear "uninitialized" in the caller — even if the callee value-initialized the struct. On the main thread stack this is harmless (OS zero-initializes pages), but on heap-allocated fiber stacks the dirty shadow can propagate via stack slot reuse, causing false positives in unrelated code.

## Files to Modify

1. **`contrib/boost-cmake/CMakeLists.txt`** - Add `BOOST_USE_MSAN` definition for memory sanitizer builds, similar to how `BOOST_USE_ASAN` and `BOOST_USE_TSAN` are handled.

2. **`src/Common/Fiber.h`** - Update the comment to mention `BOOST_USE_MSAN` alongside the other sanitizer defines.

3. **`src/Common/FiberStack.cpp`** - Update the comment above `__msan_unpoison` to explain the struct padding issue correctly (the old explanation was incomplete).

4. **`src/Common/tests/gtest_dragonbox_msan.cpp`** - Create this new test file documenting the MSan limitation with struct padding in return values.

## Key Details

- The CMake change should add an `elseif (SANITIZE MATCHES "memory")` branch that defines `BOOST_USE_MSAN` between the existing ASAN and TSAN branches.

- The Fiber.h comment should say: "BOOST_USE_ASAN, BOOST_USE_MSAN, BOOST_USE_TSAN and BOOST_USE_UCONTEXT are defined via CMake for sanitizer builds."

- The FiberStack.cpp comment should explain:
  - MSan doesn't track shadow for struct padding bytes through return values
  - The LLVM IR shadow is per-field, not per-byte of the padded representation
  - Any struct with padding returned by value will have uninitialized padding shadow in the caller
  - On heap-allocated fiber stacks the dirty shadow can propagate via stack slot reuse

- The new test file should demonstrate this MSan limitation using dragonbox's `unsigned_fp_t<double>` type (which has 4 bytes of padding after `uint64_t` + `int`).

## References

This issue is documented in several LLVM bug reports:
- llvm/llvm-project#54476 — canonical MSan bug: struct padding false positives
- llvm/llvm-project#58945 — Clang codegen does not emit writes for padding bytes

The fix ensures MSan properly tracks memory across fiber context switches and explains why `__msan_unpoison` is necessary for fiber stack allocation.
