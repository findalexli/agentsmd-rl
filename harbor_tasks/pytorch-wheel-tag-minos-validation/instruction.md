# Add Wheel Platform Tag Validation to Smoke Tests

## Problem

The PyTorch CI smoke tests (`.ci/pytorch/smoke_test/smoke_test.py`) currently validate many aspects of a built wheel — imports, basic ops, CUDA, etc. — but they do **not** validate that the wheel's platform tag metadata is correct.

This matters because:

1. **Platform tag correctness**: A wheel built for Linux x86_64 should have a platform tag matching `_x86_64`, a macOS ARM64 wheel should match `macosx_*_arm64`, etc. If the tag is wrong, pip will install the wheel on the wrong platform, causing confusing runtime failures.

2. **macOS minos consistency**: On macOS, the wheel filename encodes a minimum OS version (e.g., `macosx_11_0_arm64` means minos 11.0). The actual compiled dylibs inside the wheel should have a matching `minos` field in their Mach-O load commands (`LC_BUILD_VERSION` or `LC_VERSION_MIN_MACOSX`). A mismatch means the wheel claims compatibility with an OS version that the binaries don't actually support.

## What Needs to Be Done

1. **Create a new validation module** at `.ci/pytorch/smoke_test/check_wheel_tags.py` that:
   - Extracts `Tag:` entries from the `WHEEL` metadata inside `.whl` files (found in `PYTORCH_FINAL_PACKAGE_DIR`) or from installed package metadata
   - Validates the python tag, ABI tag, and platform tag against expected values based on `TARGET_OS`, `sys.platform`, `sys.version_info`, and `sys.abiflags`
   - On macOS, extracts `.dylib` files from the wheel to a temp directory, runs `otool -l` on each, and verifies the `minos` field matches what the wheel filename claims
   - Raises `RuntimeError` on any mismatch

2. **Integrate the new module** into `smoke_test.py` so it runs as part of the standard smoke test suite (call it from `main()`).

### Expected platform patterns by target OS

- `linux` → platform tag ends with `_x86_64`
- `linux-aarch64` → ends with `_aarch64`
- `windows`/`win32` → `win_amd64`
- `macos-arm64` → `macosx_*_arm64`
- `darwin` → `macosx_*_(arm64|x86_64)`

### Relevant files

- `.ci/pytorch/smoke_test/smoke_test.py` — the existing smoke test entry point
- The new script should live alongside it in `.ci/pytorch/smoke_test/`
