# Bug: abi3 wheel Python version treated as exact match instead of lower bound

## Context

When resolving wheel distributions, uv computes "implied markers" from wheel filenames to determine which Python versions a wheel is compatible with. This logic lives in the `implied_python_markers` function in `crates/uv-distribution-types/src/prioritized_distribution.rs`.

## Problem

Wheels built against the Python stable ABI use the `abi3` ABI tag (e.g., `cp39-abi3`). The `abi3` tag means "compatible with CPython at or above the tagged version" — so `cp39-abi3` should match CPython 3.9, 3.10, 3.11, 3.12, etc.

However, the current `implied_python_markers` function does not account for `abi3` at all. It treats the Python version tag as an exact version constraint (e.g., `cp39` becomes `python_version == '3.9.*'`), which is only correct for non-stable-ABI wheels.

This causes real-world failures: for example, a wheel like `flashinfer_jit_cache-0.5.3+cu130-cp39-abi3-manylinux_2_28_x86_64.whl` should be installable on Python 3.12, but uv's resolver rejects it because the implied marker says `python_version == '3.9.*'` rather than `python_version >= '3.9'`.

## Expected behavior

When any ABI tag on a wheel is `abi3`, the Python version tag should be interpreted as a **lower bound** (`>=`) rather than an **exact match** (`==*`). Non-abi3 wheels should continue to use exact version matching.

## Relevant code

- `crates/uv-distribution-types/src/prioritized_distribution.rs` — the `implied_python_markers` function
- The `AbiTag` enum (look for `Abi3` variant) is already available on `WheelFilename`
