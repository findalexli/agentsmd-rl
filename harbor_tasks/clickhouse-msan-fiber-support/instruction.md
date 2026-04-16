# Task: Add MSan Support for Fibers and Document Dragonbox Struct Padding Issue

## Problem

The ClickHouse codebase has issues with Memory Sanitizer (MSan) support for fiber context tracking. There are two related problems:

1. **Missing MSan fiber annotations**: The boost fiber implementation has MSan annotations (`__msan_start_switch_fiber`/`__msan_finish_switch_fiber`) around context switches, but the build system doesn't enable them for memory sanitizer builds. Without these annotations, MSan loses track of shadow memory across fiber context switches, causing false positives.

2. **Struct padding shadow tracking**: MSan tracks shadow per-field in LLVM IR, not per-byte of the padded struct representation. When a struct with padding is returned by value, the padding bytes have no shadow entry and appear "uninitialized" in the caller — even if the callee value-initialized the struct. On the main thread stack this is harmless (OS zero-initializes pages), but on heap-allocated fiber stacks the dirty shadow can propagate via stack slot reuse, causing false positives in unrelated code.

## Required Changes

### CMake Build Configuration

The file `contrib/boost-cmake/CMakeLists.txt` handles sanitizer-specific compile definitions for the `_boost_context` target. It currently enables sanitizer support for Address Sanitizer and Thread Sanitizer but lacks memory sanitizer support.

Add memory sanitizer support following the same pattern used for other sanitizers. The sanitizer definitions must appear in alphabetical order (ASAN, then MSAN, then TSAN).

### Fiber Header

The file `src/Common/Fiber.h` has an outdated comment about `defines.h` that should be included before `fiber.hpp`. This is no longer accurate and needs to be updated. The comment should explain that `BOOST_USE_MSAN`, `BOOST_USE_ASAN`, `BOOST_USE_TSAN`, and `BOOST_USE_UCONTEXT` are defined via CMake for sanitizer builds.

### FiberStack Source

The file `src/Common/FiberStack.cpp` contains a call to `__msan_unpoison(data, num_bytes)` with an explanatory comment. The current comment incorrectly explains the false positives by saying "stack slots are reused across function calls" — this explanation is wrong and must be corrected. The comment should explain the real reason: MSan doesn't track shadow for struct padding bytes through return values because it uses per-field shadow tracking in LLVM IR.

### Dragonbox MSan Test File

Create a new test file `src/Common/tests/gtest_dragonbox_msan.cpp` to document the MSan struct padding limitation. The test must:
- Be named `ReturnValuePaddingShadowIsLost` in the `DragonboxMSan` test suite
- Be guarded by a `MEMORY_SANITIZER` preprocessor check
- Use the dragonbox library
- Discuss struct padding in the test or its comments
- Demonstrate the issue using dragonbox's `unsigned_fp_t<double>` type, which has 4 bytes of padding after a `uint64_t` + `int` (total `sizeof` is 16)

## Background

This issue is documented in LLVM bug reports:
- llvm/llvm-project#54476 — canonical MSan bug: struct padding false positives
- llvm/llvm-project#58945 — Clang codegen does not emit writes for padding bytes

The `__msan_unpoison` call in FiberStack is necessary because on heap-allocated fiber stacks (unlike the OS-zero-initialized main thread stack), dirty shadow from struct padding can propagate via stack slot reuse and trigger false positives in unrelated code.
