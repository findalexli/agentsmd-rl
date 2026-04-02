# Wheel Tag Validation Fails on Free-Threaded Python Builds

## Bug Report

The CI wheel-tag validation script at `.ci/pytorch/smoke_test/check_wheel_tags.py` incorrectly rejects valid wheels when run under free-threaded Python (builds without the GIL).

### Steps to Reproduce

1. Build a PyTorch wheel on free-threaded Python 3.13t
2. The wheel filename contains the ABI tag `cp313t` (the `t` suffix indicates free-threaded)
3. Run `check_wheel_platform_tag()` — it raises an ABI tag mismatch error

### Expected Behavior

The validator should recognize that free-threaded Python uses a `t` ABI suffix and compute the expected ABI tag accordingly, even when `sys.abiflags` is empty.

### Observed Behavior

`sys.abiflags` is an empty string on free-threaded Python, so the script computes the expected ABI as `cp313` instead of `cp313t`. Any wheel built for free-threaded Python fails validation.

### Additional Issues

There is also unreachable dead code in the tag validation loop — a `continue` statement after a `raise RuntimeError(...)` that can never execute.

Additionally, the `check_mac_wheel_minos()` function only works when `PYTORCH_FINAL_PACKAGE_DIR` is set (Mode 1: reading from .whl files). Unlike `check_wheel_platform_tag()`, it has no Mode 2 fallback to check minos on an already-installed torch package. This means the minos verification is silently skipped in post-install validation scenarios on macOS.

### Relevant Files

- `.ci/pytorch/smoke_test/check_wheel_tags.py` — the `check_wheel_platform_tag()` and `check_mac_wheel_minos()` functions
