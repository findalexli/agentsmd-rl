# Wheel Tag Validation Fails on Free-Threaded Python Builds

## Bug Report

The CI wheel-tag validation script at `.ci/pytorch/smoke_test/check_wheel_tags.py` rejects valid wheels when run under free-threaded Python (builds without the GIL).

### Symptom

When `sys.abiflags` is empty (free-threaded Python), the validator computes the expected ABI tag as `cp313` instead of `cp313t`, causing all free-threaded wheels to fail validation with an ABI tag mismatch error.

### Expected Behavior

Wheels built for free-threaded Python 3.13 with the `cp313t` ABI tag must pass validation. The validator must handle free-threaded detection using available runtime and environment signals.

### Additional Issues

The tag validation loop contains unreachable code that can never execute.

Additionally, `check_mac_wheel_minos()` silently skips when `PYTORCH_FINAL_PACKAGE_DIR` is not set, rather than attempting to read dylib minos values from the installed torch package. The function output should not contain "skipping wheel minos" when operating in this fallback mode.

### Relevant Files

- `.ci/pytorch/smoke_test/check_wheel_tags.py` — the wheel tag validation functions

### What to Fix

1. **Free-threaded ABI detection**: Wheels with the `t` ABI suffix (e.g., `cp313t`) must be accepted as valid when the Python runtime is free-threaded. The validator needs to detect free-threaded builds using available system information.

2. **Dead code removal**: Remove unreachable code from the tag validation loop.

3. **Mac wheel minos fallback**: When `PYTORCH_FINAL_PACKAGE_DIR` is not set, `check_mac_wheel_minos()` should attempt to read wheel metadata from the installed torch package instead of skipping.