# Bug: Free-threaded Python not shown in built-wheel error messages

## Context

When `uv` builds a wheel from source and the resulting wheel is incompatible with the current (or target) Python platform, it reports an error like:

```
The built wheel `foo-1.0-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15 on macOS aarch64
```

## Problem

When using free-threaded Python (e.g., Python 3.14t or 3.15t), the error message does not include the `t` suffix. It reports `Python 3.15` instead of `Python 3.15t`. This makes it confusing for users running free-threaded builds, since the error message doesn't accurately reflect their Python variant.

The issue is in how the Python version is represented and displayed in the wheel-incompatibility error variants in `crates/uv-distribution/src/error.rs`. Currently the python version is stored as a simple `(u8, u8)` tuple, which has no way to carry the free-threaded information.

## Relevant files

- `crates/uv-distribution/src/error.rs` — Error enum with `BuiltWheelIncompatibleHostPlatform` and `BuiltWheelIncompatibleTargetPlatform` variants
- `crates/uv-distribution/src/distribution_database.rs` — Where these errors are constructed (around the wheel compatibility check)
- `crates/uv-platform-tags/src/tags.rs` — The `Tags` struct, which already tracks whether the interpreter is free-threaded

## Expected behavior

The error messages should show `Python 3.15t` when the interpreter is free-threaded, and `Python 3.15` for the default variant.
