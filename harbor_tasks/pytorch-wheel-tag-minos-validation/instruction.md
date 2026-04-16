# Add Wheel Platform Tag Validation to Smoke Tests

## Problem

The PyTorch CI smoke tests (`.ci/pytorch/smoke_test/smoke_test.py`) currently validate many aspects of a built wheel — imports, basic ops, CUDA, etc. — but they do **not** validate that the wheel's platform tag metadata is correct.

This matters because:

1. **Platform tag correctness**: A wheel built for Linux x86_64 should have a platform tag matching `_x86_64`, a macOS ARM64 wheel should match `macosx_*_arm64`, etc. If the tag is wrong, pip will install the wheel on the wrong platform, causing confusing runtime failures.

2. **macOS minos consistency**: On macOS, the wheel filename encodes a minimum OS version (e.g., `macosx_11_0_arm64` means minos 11.0). The actual compiled dylibs inside the wheel should have a matching `minos` field in their Mach-O load commands (`LC_BUILD_VERSION` or `LC_VERSION_MIN_MACOSX`). A mismatch means the wheel claims compatibility with an OS version that the binaries don't actually support.

## What Needs to Be Done

1. **Create a new validation module** at `.ci/pytorch/smoke_test/check_wheel_tags.py` that:
   - Provides a function `_extract_wheel_tags(whl_path)` that reads a `.whl` file path and returns a list of tag strings extracted from the `WHEEL` metadata entry inside the archive (e.g. `["cp312-cp312-linux_x86_64", "cp312-cp312-manylinux_2_17_x86_64"]`). If the archive contains no `WHEEL` file, return an empty list.
   - Contains a module-level dict `EXPECTED_PLATFORM_TAGS` mapping target-OS keys to regex patterns:
     - `"linux"` → pattern matching strings ending with `_x86_64`
     - `"linux-aarch64"` → pattern matching strings ending with `_aarch64`
     - `"windows"` and `"win32"` → pattern matching `win_amd64`
     - `"macos-arm64"` → pattern matching `macosx_\d+_\d+_arm64`
     - `"darwin"` → pattern matching `macosx_\d+_\d+_(arm64|x86_64)`
   - Provides a function `check_wheel_platform_tag()` that validates wheel tags:
     - Reads the single `torch-*.whl` file from the directory in env var `PYTORCH_FINAL_PACKAGE_DIR` (if set) or from the installed torch package metadata (if not set)
     - Raises `RuntimeError` if more than one torch wheel is found in that directory
     - Validates each tag's python tag, ABI tag, and platform tag
     - Each tag must be exactly in the format `<python>-<abi>-<platform>` (three dash-separated parts). Malformed tags — including but not limited to:
       - `cp312-linux_x86_64` (only one part, missing ABI and platform)
       - `cp312` (only one part)
       - `cp312-cp312-linux_x86_64-extra` (four parts, an extra component after the platform)
       must be rejected with a `RuntimeError`
     - Raises `RuntimeError` on any mismatch
   - Provides a function `check_mac_wheel_minos()` that on macOS extracts dylibs from the wheel, runs `otool -l` on each, and verifies the `minos` field matches the wheel filename's OS version
   - Raises `RuntimeError` on any mismatch

2. **Integrate the new module** into `smoke_test.py` by:
   - Importing `check_wheel_platform_tag` and `check_mac_wheel_minos` from `check_wheel_tags`
   - Calling both functions from `main()`

3. **Code quality requirements**:
   - All functions in `check_wheel_tags.py` must be genuine implementations with at least 3 statements in the function body beyond the docstring (no stub functions)
   - The code in `.ci/pytorch/smoke_test/` must pass `ruff check` linting with no errors
   - The script `.ci/pytorch/check_binary.sh` must pass `shellcheck` validation with no errors
