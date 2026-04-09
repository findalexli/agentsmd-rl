# Implement PEP 803: abi3t stable ABI for free-threaded CPython

## Problem

uv does not recognize the `abi3t` ABI tag introduced by PEP 803. This means:

1. Wheel filenames containing `abi3t` (e.g., `foo-1.2.3-cp315-abi3t-manylinux_2_17_x86_64.whl`) fail to parse — the ABI tag is rejected as unknown.
2. Free-threaded CPython (3.15+) cannot use stable ABI wheels because no `abi3t` tags are generated in the platform tag list.
3. Compatibility checks reject `abi3t` wheels on free-threaded Python, even though PEP 803 designates `abi3t` as the stable ABI for free-threaded builds.

## Expected Behavior

- `abi3t` should be recognized as a valid ABI tag, similar to the existing `abi3` tag.
- `abi3t` should be classified as a "stable ABI" alongside `abi3`, so that code checking for stable ABI compatibility handles both.
- Free-threaded CPython 3.15+ should generate `abi3t` tags in its platform tag list (note: `abi3t` starts at Python 3.15, whereas `abi3` starts at 3.2).
- Wheel compatibility checks on free-threaded Python should accept `abi3t` wheels.

## Files to Look At

- `crates/uv-platform-tags/src/abi_tag.rs` — defines the `AbiTag` enum, parsing (`FromStr`), and display
- `crates/uv-platform-tags/src/tags.rs` — generates platform tags and checks wheel compatibility
- `crates/uv-distribution-types/src/prioritized_distribution.rs` — checks stable ABI for implied Python markers
- `crates/uv-distribution-types/src/requires_python.rs` — checks ABI tag compatibility with requires-python
- `crates/uv-distribution-filename/src/wheel.rs` — parses wheel filenames including ABI tags
